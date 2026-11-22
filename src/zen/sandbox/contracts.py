"""Typed contracts between the sandbox runtime and an OS isolation backend."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Protocol


REQUIRED_CONTROLS = frozenset({
    "process_isolation",
    "filesystem_isolation",
    "network_isolation",
    "resource_limits",
    "secret_isolation",
})


@dataclass(frozen=True, slots=True)
class SandboxRequest:
    argv: tuple[str, ...]
    cwd: Path
    environment: Mapping[str, str] = field(default_factory=dict)
    stdin: bytes = b""


@dataclass(frozen=True, slots=True)
class CapabilityReport:
    """Backend's evidence-backed list of controls it can enforce."""

    enforced_controls: frozenset[str]
    evidence: str = ""

    @property
    def missing_controls(self) -> frozenset[str]:
        return REQUIRED_CONTROLS - self.enforced_controls


@dataclass(frozen=True, slots=True)
class SandboxResult:
    exit_code: int
    stdout: bytes = b""
    stderr: bytes = b""
    timed_out: bool = False


class SandboxBackend(Protocol):
    """OS-specific backend. Implementations must enforce, not merely simulate."""

    def probe(self, policy: object) -> CapabilityReport:
        """Return controls proven available for this exact host and policy."""
        ...

    def execute(self, request: SandboxRequest, policy: object) -> SandboxResult:
        """Execute without inheriting parent credentials or ambient authority."""
        ...


class SandboxUnavailableError(RuntimeError):
    """Raised when required isolation cannot be proven."""


class SandboxExecutionError(RuntimeError):
    """Raised when backend output violates the declared execution contract."""
