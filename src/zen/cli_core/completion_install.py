from __future__ import annotations

import os
import secrets
import shlex
import stat
from dataclasses import dataclass
from pathlib import Path


class CompletionInstallError(Exception):
    """Raised when shell completion cannot be safely installed or removed."""


_START = "# >>> ZEN completion (managed) >>>"
_END = "# <<< ZEN completion (managed) <<<"

_FILE_MARKERS = {
    "bash": "# ZEN-COMPLETION-MANAGED: bash",
    "zsh": "# ZEN-COMPLETION-MANAGED: zsh",
}

_DIR_FLAGS = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
_FILE_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)


@dataclass(frozen=True)
class _FileSnapshot:
    content: str
    mode: int


def _paths(shell: str) -> tuple[Path, Path]:
    if shell not in ("bash", "zsh"):
        raise CompletionInstallError(f"unsupported shell: {shell}")

    home = Path.home()
    data_home = Path(os.environ.get("XDG_DATA_HOME", home / ".local/share"))
    if not data_home.is_absolute():
        raise CompletionInstallError("XDG_DATA_HOME must be an absolute path")

    completion_dir = data_home / "zen" / "completions"
    completion_file = completion_dir / ("zen.bash" if shell == "bash" else "_zen")

    if shell == "bash":
        rc_file = home / ".bashrc"
    else:
        zdotdir = Path(os.environ.get("ZDOTDIR") or home)
        if not zdotdir.is_absolute():
            raise CompletionInstallError("ZDOTDIR must be an absolute path")
        rc_file = zdotdir / ".zshrc"

    return completion_file, rc_file


def _open_parent(path: Path, *, create: bool) -> int:
    """Open the target parent from an accessible common ancestor.

    Android/Termux may deny opening filesystem root ("/"). Using the common
    ancestor of the target parent and the current home directory avoids that
    assumption while retaining O_NOFOLLOW checks for every traversed component
    below the anchor. The anchor and its ancestry are the platform trust boundary.
    """
    if not path.is_absolute():
        raise CompletionInstallError(f"path must be absolute: {path}")

    try:
        anchor = Path(os.path.commonpath((str(path.parent), str(Path.home()))))
        relative_parent = path.parent.relative_to(anchor)
    except (OSError, ValueError) as exc:
        raise CompletionInstallError(
            f"cannot determine a safe directory anchor for {path}: {exc}"
        ) from exc

    fd = -1
    try:
        fd = os.open(anchor, _DIR_FLAGS)
        for component in relative_parent.parts:
            if component in ("", "."):
                continue
            try:
                next_fd = os.open(component, _DIR_FLAGS, dir_fd=fd)
            except FileNotFoundError:
                if not create:
                    raise
                try:
                    os.mkdir(component, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
                next_fd = os.open(component, _DIR_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except Exception:
        if fd >= 0:
            os.close(fd)
        raise


def _read_snapshot(path: Path) -> _FileSnapshot | None:
    parent_fd = -1
    file_fd = -1
    try:
        parent_fd = _open_parent(path, create=False)
        file_fd = os.open(
            path.name, os.O_RDONLY | _FILE_NOFOLLOW, dir_fd=parent_fd
        )
        info = os.fstat(file_fd)
        if not stat.S_ISREG(info.st_mode):
            raise CompletionInstallError(f"not a regular file: {path}")

        chunks: list[bytes] = []
        while True:
            chunk = os.read(file_fd, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        try:
            content = b"".join(chunks).decode("utf-8")
        except UnicodeError as exc:
            raise CompletionInstallError(f"cannot decode {path}: {exc}") from exc
        return _FileSnapshot(content, stat.S_IMODE(info.st_mode))
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise CompletionInstallError(f"cannot safely read {path}: {exc}") from exc
    finally:
        if file_fd >= 0:
            os.close(file_fd)
        if parent_fd >= 0:
            os.close(parent_fd)


def _read_text(path: Path) -> str | None:
    snapshot = _read_snapshot(path)
    return None if snapshot is None else snapshot.content


def _unlink(path: Path, *, missing_ok: bool = False) -> None:
    parent_fd = -1
    try:
        parent_fd = _open_parent(path, create=False)
        try:
            info = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            if missing_ok:
                return
            raise
        if not stat.S_ISREG(info.st_mode):
            raise CompletionInstallError(f"refusing to remove non-regular file: {path}")
        os.unlink(path.name, dir_fd=parent_fd)
        os.fsync(parent_fd)
    except FileNotFoundError:
        if not missing_ok:
            raise
    except OSError as exc:
        raise CompletionInstallError(f"cannot safely remove {path}: {exc}") from exc
    finally:
        if parent_fd >= 0:
            os.close(parent_fd)


def _atomic_write(
    path: Path, content: str, *, mode_override: int | None = None
) -> None:
    parent_fd = -1
    temporary: str | None = None
    file_fd = -1
    try:
        parent_fd = _open_parent(path, create=True)
        try:
            existing = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            mode = 0o600 if mode_override is None else mode_override
        else:
            if not stat.S_ISREG(existing.st_mode):
                raise CompletionInstallError(
                    f"refusing to replace non-regular file: {path}"
                )
            mode = (
                stat.S_IMODE(existing.st_mode)
                if mode_override is None
                else mode_override
            )

        for _ in range(10):
            candidate = f".{path.name}.{secrets.token_hex(8)}.tmp"
            try:
                file_fd = os.open(
                    candidate,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | _FILE_NOFOLLOW,
                    0o600,
                    dir_fd=parent_fd,
                )
                temporary = candidate
                break
            except FileExistsError:
                continue
        if file_fd < 0 or temporary is None:
            raise CompletionInstallError(
                f"cannot allocate temporary file for {path}"
            )

        data = content.encode("utf-8")
        view = memoryview(data)
        while view:
            written = os.write(file_fd, view)
            if written <= 0:
                raise OSError("short write while writing temporary file")
            view = view[written:]

        os.fchmod(file_fd, mode)
        os.fsync(file_fd)
        os.close(file_fd)
        file_fd = -1

        os.rename(
            temporary,
            path.name,
            src_dir_fd=parent_fd,
            dst_dir_fd=parent_fd,
        )
        temporary = None
        os.fsync(parent_fd)
    except CompletionInstallError:
        raise
    except OSError as exc:
        raise CompletionInstallError(
            f"cannot safely write {path}: {exc}"
        ) from exc
    finally:
        if file_fd >= 0:
            os.close(file_fd)
        if temporary is not None and parent_fd >= 0:
            try:
                os.unlink(temporary, dir_fd=parent_fd)
            except OSError:
                pass
        if parent_fd >= 0:
            os.close(parent_fd)


def _managed_block(shell: str, completion_file: Path) -> str:
    source = shlex.quote(str(completion_file))
    if shell == "bash":
        body = f"[ -r {source} ] && source {source}"
    else:
        body = (
            "autoload -Uz compinit\n"
            "compinit\n"
            f"[ -r {source} ] && source {source}"
        )
    return f"{_START}\n{body}\n{_END}"


def _replace_managed_block(current: str, block: str) -> str:
    start_count = current.count(_START)
    end_count = current.count(_END)
    if start_count != end_count or start_count > 1:
        raise CompletionInstallError(
            "invalid or duplicate ZEN markers in shell config"
        )
    if start_count == 1:
        start = current.index(_START)
        end = current.index(_END) + len(_END)
        if end < start:
            raise CompletionInstallError("invalid ZEN marker order")
        return current[:start] + block + current[end:]
    return current + "\n" + block + "\n"


def _remove_managed_block(current: str) -> str:
    start_count = current.count(_START)
    end_count = current.count(_END)
    if start_count == 0 and end_count == 0:
        return current
    if start_count != 1 or end_count != 1:
        raise CompletionInstallError(
            "invalid or duplicate ZEN markers in shell config"
        )
    start = current.index(_START)
    end = current.index(_END) + len(_END)
    if end < start:
        raise CompletionInstallError("invalid ZEN marker order")
    prefix = current[:start]
    suffix = current[end:]
    if prefix.endswith("\n"):
        prefix = prefix[:-1]
    if suffix.startswith("\n"):
        suffix = suffix[1:]
    return prefix + suffix


def _is_owned_file(content: str | None, shell: str) -> bool:
    if content is None:
        return False
    lines = content.splitlines()
    if shell == "zsh":
        return (
            len(lines) >= 2
            and lines[0] == "#compdef zen"
            and lines[1] == _FILE_MARKERS[shell]
        )
    return bool(lines and lines[0] == _FILE_MARKERS[shell])


def _rollback_error(
    operation: str, original: Exception, rollback_errors: list[Exception]
) -> CompletionInstallError:
    details = "; ".join(str(error) for error in rollback_errors)
    return CompletionInstallError(
        f"{operation} failed ({original}); rollback also failed ({details}). "
        "Inspect the shell config and ZEN completion file before retrying."
    )


def _restore_snapshot(path: Path, snapshot: _FileSnapshot | None) -> None:
    if snapshot is None:
        _unlink(path, missing_ok=True)
    else:
        _atomic_write(path, snapshot.content, mode_override=snapshot.mode)


def _rollback_paths(
    operation: str,
    original: Exception,
    changed: list[tuple[Path, _FileSnapshot | None]],
) -> None:
    errors: list[Exception] = []
    for path, snapshot in reversed(changed):
        try:
            _restore_snapshot(path, snapshot)
        except Exception as exc:
            errors.append(exc)
    if errors:
        raise _rollback_error(operation, original, errors) from original


def install_completion(shell: str, script: str) -> None:
    completion_file, rc_file = _paths(shell)
    if not script.endswith("\n"):
        script += "\n"

    if shell == "zsh":
        script_lines = script.splitlines()
        if not script_lines or script_lines[0] != "#compdef zen":
            raise CompletionInstallError(
                "Zsh completion script must start with '#compdef zen'"
            )
        managed_script = (
            script_lines[0]
            + "\n"
            + _FILE_MARKERS[shell]
            + "\n"
            + "\n".join(script_lines[1:])
            + "\n"
        )
    else:
        managed_script = _FILE_MARKERS[shell] + "\n" + script

    old_completion = _read_snapshot(completion_file)
    old_rc = _read_snapshot(rc_file)
    old_completion_text = (
        None if old_completion is None else old_completion.content
    )
    old_rc_text = None if old_rc is None else old_rc.content

    if old_completion_text is not None and not _is_owned_file(
        old_completion_text, shell
    ):
        raise CompletionInstallError(
            f"refusing to overwrite file not owned by ZEN: {completion_file}"
        )

    new_rc = _replace_managed_block(
        old_rc_text or "", _managed_block(shell, completion_file)
    )

    changed: list[tuple[Path, _FileSnapshot | None]] = []
    try:
        changed.append((completion_file, old_completion))
        _atomic_write(completion_file, managed_script)
        changed.append((rc_file, old_rc))
        _atomic_write(rc_file, new_rc)
    except Exception as original:
        _rollback_paths("installation", original, changed)
        raise


def uninstall_completion(shell: str) -> None:
    completion_file, rc_file = _paths(shell)
    old_completion = _read_snapshot(completion_file)
    old_rc = _read_snapshot(rc_file)
    old_completion_text = (
        None if old_completion is None else old_completion.content
    )
    old_rc_text = None if old_rc is None else old_rc.content

    if old_completion_text is not None and not _is_owned_file(
        old_completion_text, shell
    ):
        raise CompletionInstallError(
            f"refusing to remove file not owned by ZEN: {completion_file}"
        )

    new_rc = _remove_managed_block(old_rc_text or "")
    changed: list[tuple[Path, _FileSnapshot | None]] = []
    try:
        if old_rc is not None and new_rc != old_rc_text:
            changed.append((rc_file, old_rc))
            _atomic_write(rc_file, new_rc)
        if old_completion is not None:
            changed.append((completion_file, old_completion))
            _unlink(completion_file)
    except Exception as original:
        _rollback_paths("uninstallation", original, changed)
        raise
