"""Fail-closed orchestration for ZEAI sandbox workloads.

No backend is bundled yet. Until a reviewed OS backend proves every required
control, workloads are rejected rather than executed with weaker isolation.
"""
from pathlib import Path
from typing import Mapping

from .contracts import (
    SandboxBackend,
    SandboxExecutionError,
    SandboxOutputCollector,
    SandboxRequest,
    SandboxResult,
    SandboxUnavailableError,
)
from .policy import SandboxPolicy


_BLOCKED_ENV_MARKERS = (
    "SECRET", "TOKEN", "PASSWORD", "PRIVATE", "CREDENTIAL", "API_KEY",
    "AUTH", "GITHUB", "SSH", "AWS", "AZURE", "GOOGLE_APPLICATION",
)


def _safe_environment(
    values: Mapping[str, str],
    policy: SandboxPolicy,
) -> dict[str, str]:
    if not isinstance(values, Mapping):
        raise ValueError("environment must be a mapping")

    if len(values) > policy.max_environment_count:
        raise ValueError("environment variable count exceeds the configured limit")

    safe: dict[str, str] = {}
    total_bytes = 0

    for key, value in values.items():
        if not isinstance(key, str) or not key or not key.isidentifier():
            raise ValueError("invalid environment variable name")

        normalized = key.upper()
        if any(marker in normalized for marker in _BLOCKED_ENV_MARKERS):
            raise ValueError(
                f"sensitive environment variable is forbidden: {key}"
            )

        if key not in policy.allowed_environment:
            raise ValueError(
                f"environment variable is not allowlisted: {key}"
            )

        if not isinstance(value, str) or "\\x00" in value:
            raise ValueError(f"invalid environment value for: {key}")

        try:
            key_size = len(key.encode("utf-8"))
            value_size = len(value.encode("utf-8"))
        except UnicodeEncodeError as exc:
            raise ValueError("environment contains invalid Unicode") from exc

        if value_size > policy.max_environment_value_bytes:
            raise ValueError(
                f"environment value exceeds the configured limit: {key}"
            )

        total_bytes += key_size + value_size
        if total_bytes > policy.max_environment_total_bytes:
            raise ValueError(
                "total environment size exceeds the configured limit"
            )

        safe[key] = value

    return safe


class SandboxRuntime:
    """Validate a request, prove isolation, then delegate to a trusted backend."""

    def __init__(
        self,
        policy: SandboxPolicy,
        backend: SandboxBackend | None = None,
    ):
        self.policy = policy
        self.backend = backend

    def run(
        self,
        argv: tuple[str, ...] | list[str],
        *,
        cwd: str | Path,
        environment: Mapping[str, str] | None = None,
        stdin: bytes = b"",
    ) -> SandboxResult:
        if self.backend is None:
            raise SandboxUnavailableError(
                "no reviewed OS isolation backend is configured"
            )

        if not isinstance(argv, (tuple, list)):
            raise ValueError(
                "argv must be a tuple or list of arguments, not a shell command string"
            )

        if not argv:
            raise ValueError("argv must contain at least one argument")

        if len(argv) > self.policy.max_argv_count:
            raise ValueError("argv count exceeds the configured limit")

        command_items: list[str] = []
        total_argv_bytes = 0

        for arg in argv:
            if not isinstance(arg, str) or not arg or "\\x00" in arg:
                raise ValueError("argv must contain non-empty strings")

            try:
                arg_size = len(arg.encode("utf-8"))
            except UnicodeEncodeError as exc:
                raise ValueError("argv contains invalid Unicode") from exc

            if arg_size > self.policy.max_argv_item_bytes:
                raise ValueError("an argv item exceeds the configured limit")

            total_argv_bytes += arg_size
            if total_argv_bytes > self.policy.max_argv_total_bytes:
                raise ValueError("total argv size exceeds the configured limit")

            command_items.append(arg)

        command = tuple(command_items)
        workdir = Path(cwd).expanduser().resolve()

        if not self.policy.contains_path(workdir) or not workdir.is_dir():
            raise ValueError(
                "cwd must be an existing directory inside workspace_root"
            )

        if not isinstance(stdin, bytes):
            raise ValueError("stdin must be bytes")

        if len(stdin) > self.policy.max_stdin_bytes:
            raise ValueError("stdin exceeds the configured size limit")

        safe_env = _safe_environment(
            {} if environment is None else environment,
            self.policy,
        )
        request = SandboxRequest(command, workdir, safe_env, stdin)

        report = self.backend.probe(self.policy)
        missing = report.missing_controls

        if missing:
            names = ", ".join(sorted(missing))
            raise SandboxUnavailableError(
                f"required isolation controls are unproven: {names}"
            )

        if not report.evidence.strip():
            raise SandboxUnavailableError(
                "backend supplied no evidence for its isolation capability report"
            )

        output = SandboxOutputCollector(self.policy.max_output_bytes)
        result = self.backend.execute(request, self.policy, output)

        if not isinstance(result, SandboxResult):
            raise SandboxExecutionError(
                "backend returned an invalid result type"
            )

        if (
            not isinstance(result.stdout, bytes)
            or not isinstance(result.stderr, bytes)
        ):
            raise SandboxExecutionError(
                "backend output streams must be bytes"
            )

        if result.stdout or result.stderr:
            raise SandboxExecutionError(
                "backend must stream output through SandboxOutputCollector"
            )

        return SandboxResult(
            result.exit_code,
            output.stdout,
            output.stderr,
            result.timed_out,
        )
