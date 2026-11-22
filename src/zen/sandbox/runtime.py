"""Fail-closed orchestration for ZEAI sandbox workloads.

No backend is bundled yet. Until a reviewed OS backend proves every required
control, workloads are rejected rather than executed with weaker isolation.
"""
from pathlib import Path
from typing import Mapping

from .contracts import (
    SandboxBackend,
    SandboxExecutionError,
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
    safe: dict[str, str] = {}

    for key, value in values.items():
        normalized = key.upper()

        if any(marker in normalized for marker in _BLOCKED_ENV_MARKERS):
            raise ValueError(
                f"sensitive environment variable is forbidden: {key}"
            )

        if key not in policy.allowed_environment:
            raise ValueError(
                f"environment variable is not allowlisted: {key}"
            )

        if not isinstance(value, str) or "\x00" in value:
            raise ValueError(f"invalid environment value for: {key}")

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

        if isinstance(argv, str):
            raise ValueError(
                "argv must be a sequence of arguments, not a shell command string"
            )

        command = tuple(argv)

        if not command or any(
            not isinstance(arg, str) or not arg or "\x00" in arg
            for arg in command
        ):
            raise ValueError(
                "argv must contain non-empty strings"
            )

        workdir = Path(cwd).expanduser().resolve()

        if not self.policy.contains_path(workdir) or not workdir.is_dir():
            raise ValueError(
                "cwd must be an existing directory inside workspace_root"
            )

        if not isinstance(stdin, bytes):
            raise ValueError("stdin must be bytes")

        safe_env = _safe_environment(environment or {}, self.policy)
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

        result = self.backend.execute(request, self.policy)

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

        if (
            len(result.stdout) > self.policy.max_output_bytes
            or len(result.stderr) > self.policy.max_output_bytes
        ):
            raise SandboxExecutionError(
                "backend exceeded the configured output limit"
            )

        return result
