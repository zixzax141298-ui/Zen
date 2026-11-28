from pathlib import Path
import os
import stat

import pytest

from zen.cli_core import completion_install as installer


@pytest.fixture
def isolated_home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    data_home = tmp_path / "data"
    home.mkdir()
    data_home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    monkeypatch.setenv("XDG_DATA_HOME", str(data_home))
    monkeypatch.delenv("ZDOTDIR", raising=False)
    return home, data_home


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_install_and_uninstall_preserve_user_config(shell, isolated_home):
    home, data_home = isolated_home
    if shell == "bash":
        rc_file = home / ".bashrc"
        script = "# bash completion script\n"
    else:
        rc_file = home / ".zshrc"
        script = "#compdef zen\n# zsh completion script\n"

    original_config = "# user configuration\nexport USER_SETTING=1\n"
    rc_file.write_text(original_config, encoding="utf-8")
    installer.install_completion(shell, script)
    installed = rc_file.read_text(encoding="utf-8")
    assert installed.startswith(original_config)
    assert installed.count(installer._START) == 1
    assert installed.count(installer._END) == 1

    completion_file = (
        data_home / "zen" / "completions"
        / ("zen.bash" if shell == "bash" else "_zen")
    )
    installed_script = completion_file.read_text(encoding="utf-8")
    if shell == "zsh":
        assert installed_script.splitlines()[0] == "#compdef zen"
        assert installed_script.splitlines()[1] == installer._FILE_MARKERS[shell]

    installer.install_completion(shell, script)
    repeated = rc_file.read_text(encoding="utf-8")
    assert repeated.count(installer._START) == 1
    assert repeated.count(installer._END) == 1

    installer.uninstall_completion(shell)
    assert rc_file.read_text(encoding="utf-8") == original_config
    assert not completion_file.exists()


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_install_refuses_to_overwrite_unowned_completion_file(
    shell, isolated_home
):
    _, data_home = isolated_home
    completion_dir = data_home / "zen" / "completions"
    completion_dir.mkdir(parents=True)
    filename = "zen.bash" if shell == "bash" else "_zen"
    completion_file = completion_dir / filename
    original = "user-owned completion file\n"
    completion_file.write_text(original, encoding="utf-8")
    script = "#compdef zen\n" if shell == "zsh" else "# bash completion script\n"

    with pytest.raises(installer.CompletionInstallError):
        installer.install_completion(shell, script)
    assert completion_file.read_text(encoding="utf-8") == original


def test_install_rejects_symlink_completion_file(isolated_home, tmp_path):
    _, data_home = isolated_home
    completion_dir = data_home / "zen" / "completions"
    completion_dir.mkdir(parents=True)
    target = tmp_path / "outside.txt"
    target.write_text("outside data\n", encoding="utf-8")
    completion_file = completion_dir / "zen.bash"
    completion_file.symlink_to(target)

    with pytest.raises(installer.CompletionInstallError):
        installer.install_completion("bash", "# completion\n")
    assert target.read_text(encoding="utf-8") == "outside data\n"


def test_install_rejects_symlink_data_directory(
    isolated_home, tmp_path, monkeypatch
):
    home, _ = isolated_home
    real_data = tmp_path / "real-data"
    real_data.mkdir()
    linked_data = tmp_path / "linked-data"
    linked_data.symlink_to(real_data, target_is_directory=True)
    monkeypatch.setenv("XDG_DATA_HOME", str(linked_data))

    with pytest.raises(installer.CompletionInstallError):
        installer.install_completion("bash", "# completion\n")
    assert list(real_data.iterdir()) == []
    assert not (home / ".bashrc").exists()


def test_install_rejects_invalid_zsh_completion_header(isolated_home):
    with pytest.raises(installer.CompletionInstallError):
        installer.install_completion("zsh", "# not a compdef\n")


def test_install_rejects_duplicate_config_markers(isolated_home):
    home, _ = isolated_home
    rc_file = home / ".bashrc"
    rc_file.write_text(
        installer._START + "\n"
        + installer._END + "\n"
        + installer._START + "\n"
        + installer._END + "\n",
        encoding="utf-8",
    )
    with pytest.raises(installer.CompletionInstallError):
        installer.install_completion("bash", "# completion\n")


def test_failed_config_write_rolls_back_completion_file(isolated_home, monkeypatch):
    home, data_home = isolated_home
    rc_file = home / ".bashrc"
    original_config = "# existing user config\n"
    rc_file.write_text(original_config, encoding="utf-8")
    original_atomic_write = installer._atomic_write
    calls = 0

    def fail_config_write(path, content, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise installer.CompletionInstallError("simulated config write failure")
        return original_atomic_write(path, content, **kwargs)

    monkeypatch.setattr(installer, "_atomic_write", fail_config_write)
    with pytest.raises(installer.CompletionInstallError):
        installer.install_completion("bash", "# completion\n")

    completion_file = data_home / "zen" / "completions" / "zen.bash"
    assert not completion_file.exists()
    assert rc_file.read_text(encoding="utf-8") == original_config


def _bash_paths(home, data_home):
    return data_home / "zen" / "completions" / "zen.bash", home / ".bashrc"


def test_install_rolls_back_both_files_if_config_write_fails_after_replace(
    isolated_home, monkeypatch
):
    home, data_home = isolated_home
    completion_file, rc_file = _bash_paths(home, data_home)
    original_config = "# original config\n"
    rc_file.write_text(original_config, encoding="utf-8")
    original_write = installer._atomic_write
    failed_once = False

    def fail_after_rc_replace(path, content, **kwargs):
        nonlocal failed_once
        result = original_write(path, content, **kwargs)
        if path == rc_file and not failed_once:
            failed_once = True
            raise installer.CompletionInstallError("simulated post-replace failure")
        return result

    monkeypatch.setattr(installer, "_atomic_write", fail_after_rc_replace)
    with pytest.raises(installer.CompletionInstallError, match="post-replace"):
        installer.install_completion("bash", "# completion\n")

    assert not completion_file.exists()
    assert rc_file.read_text(encoding="utf-8") == original_config


def test_uninstall_rolls_back_both_files_if_config_write_fails_after_replace(
    isolated_home, monkeypatch
):
    home, data_home = isolated_home
    completion_file, rc_file = _bash_paths(home, data_home)
    original_config = "# original config\n"
    rc_file.write_text(original_config, encoding="utf-8")
    installer.install_completion("bash", "# completion\n")
    installed_config = rc_file.read_text(encoding="utf-8")
    installed_script = completion_file.read_text(encoding="utf-8")
    original_write = installer._atomic_write
    failed_once = False

    def fail_after_rc_replace(path, content, **kwargs):
        nonlocal failed_once
        result = original_write(path, content, **kwargs)
        if path == rc_file and not failed_once:
            failed_once = True
            raise installer.CompletionInstallError("simulated uninstall config failure")
        return result

    monkeypatch.setattr(installer, "_atomic_write", fail_after_rc_replace)
    with pytest.raises(installer.CompletionInstallError, match="uninstall config failure"):
        installer.uninstall_completion("bash")

    assert rc_file.read_text(encoding="utf-8") == installed_config
    assert completion_file.read_text(encoding="utf-8") == installed_script


def test_uninstall_restores_both_files_if_unlink_fails_after_removal(
    isolated_home, monkeypatch
):
    home, data_home = isolated_home
    completion_file, rc_file = _bash_paths(home, data_home)
    original_config = "# original config\n"
    rc_file.write_text(original_config, encoding="utf-8")
    installer.install_completion("bash", "# completion\n")
    installed_config = rc_file.read_text(encoding="utf-8")
    installed_script = completion_file.read_text(encoding="utf-8")
    original_unlink = installer._unlink

    def unlink_then_fail(path, *, missing_ok=False):
        original_unlink(path, missing_ok=missing_ok)
        raise installer.CompletionInstallError("simulated post-unlink failure")

    monkeypatch.setattr(installer, "_unlink", unlink_then_fail)
    with pytest.raises(installer.CompletionInstallError, match="post-unlink"):
        installer.uninstall_completion("bash")

    assert rc_file.read_text(encoding="utf-8") == installed_config
    assert completion_file.read_text(encoding="utf-8") == installed_script


def test_rollback_failure_is_reported(isolated_home, monkeypatch):
    home, _ = isolated_home
    rc_file = home / ".bashrc"
    rc_file.write_text("# original config\n", encoding="utf-8")
    original_write = installer._atomic_write
    calls = 0

    def fail_config_and_rollback(path, content, **kwargs):
        nonlocal calls
        calls += 1
        if path == rc_file:
            raise installer.CompletionInstallError("primary failure")
        if calls > 2:
            raise installer.CompletionInstallError("rollback failure")
        return original_write(path, content, **kwargs)

    original_unlink = installer._unlink

    def fail_rollback_unlink(path, *, missing_ok=False):
        raise installer.CompletionInstallError("rollback cleanup failure")

    monkeypatch.setattr(installer, "_atomic_write", fail_config_and_rollback)
    monkeypatch.setattr(installer, "_unlink", fail_rollback_unlink)
    with pytest.raises(installer.CompletionInstallError, match="rollback also failed"):
        installer.install_completion("bash", "# completion\n")


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_cli_install_uninstall_round_trip(tmp_path, monkeypatch, capsys, shell):
    from zen.cli import main

    home = tmp_path / "home"
    data_home = tmp_path / "data"
    home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    monkeypatch.setenv("XDG_DATA_HOME", str(data_home))
    monkeypatch.delenv("ZDOTDIR", raising=False)

    if shell == "bash":
        rc_file = home / ".bashrc"
    else:
        zdotdir = home / "zsh-config"
        zdotdir.mkdir()
        monkeypatch.setenv("ZDOTDIR", str(zdotdir))
        rc_file = zdotdir / ".zshrc"

    original_config = "# User shell configuration\nexport USER_SETTING=1\n"
    rc_file.write_text(original_config, encoding="utf-8")
    assert main(["completion", shell, "--install"]) == 0
    install_output = capsys.readouterr()
    assert f"ZEN {shell} completion installed." in install_output.out
    assert install_output.err == ""

    completion_file = (
        data_home / "zen" / "completions"
        / ("zen.bash" if shell == "bash" else "_zen")
    )
    assert completion_file.is_file()
    installed_script = completion_file.read_text(encoding="utf-8")
    if shell == "bash":
        assert installed_script.startswith(
            "# ZEN-COMPLETION-MANAGED: bash\n"
        )
    else:
        assert installed_script.startswith(
            "#compdef zen\n# ZEN-COMPLETION-MANAGED: zsh\n"
        )

    installed_config = rc_file.read_text(encoding="utf-8")
    assert installer._START in installed_config
    assert installer._END in installed_config

    assert main(["completion", shell, "--uninstall"]) == 0
    uninstall_output = capsys.readouterr()
    assert f"ZEN {shell} completion uninstalled." in uninstall_output.out
    assert uninstall_output.err == ""
    assert rc_file.read_text(encoding="utf-8") == original_config
    assert not completion_file.exists()


def test_cli_rejects_install_and_uninstall_together():
    from zen.cli import main

    with pytest.raises(SystemExit) as exc:
        main(["completion", "bash", "--install", "--uninstall"])
    assert exc.value.code == 2


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_existing_rc_permissions_are_preserved(shell, isolated_home):
    home, _ = isolated_home
    rc_file = home / (".bashrc" if shell == "bash" else ".zshrc")
    rc_file.write_text("# user config\n", encoding="utf-8")
    rc_file.chmod(0o600)

    script = "# bash completion\n" if shell == "bash" else "#compdef zen\n# zsh completion\n"
    installer.install_completion(shell, script)
    assert stat.S_IMODE(rc_file.stat().st_mode) == 0o600

    installer.uninstall_completion(shell)
    assert stat.S_IMODE(rc_file.stat().st_mode) == 0o600


def test_install_rejects_non_regular_completion_destination(isolated_home):
    _, data_home = isolated_home
    completion_dir = data_home / "zen" / "completions"
    completion_dir.mkdir(parents=True)
    (completion_dir / "zen.bash").mkdir()

    with pytest.raises(installer.CompletionInstallError):
        installer.install_completion("bash", "# completion\n")
