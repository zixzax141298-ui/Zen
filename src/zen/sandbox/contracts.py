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


class SandboxOutputCollector:
    """Thread-safe bounded collector for streamed backend output."""

    def __init__(self, max_output_bytes: int):
        from threading import Lock

        if (
            isinstance(max_output_bytes, bool)
            or not isinstance(max_output_bytes, int)
            or max_output_bytes <= 0
        ):
            raise ValueError("max_output_bytes must be a positive integer")

        self._limit = max_output_bytes
        self._stdout = bytearray()
        self._stderr = bytearray()
        self._exceeded = False
        self._lock = Lock()

    @property
    def stdout(self) -> bytes:
        with self._lock:
            return bytes(self._stdout)

    @property
    def stderr(self) -> bytes:
        with self._lock:
            return bytes(self._stderr)

    @property
    def exceeded(self) -> bool:
        with self._lock:
            return self._exceeded

    def write_stdout(self, chunk: bytes) -> None:
        self._write(self._stdout, chunk)

    def write_stderr(self, chunk: bytes) -> None:
        self._write(self._stderr, chunk)

    def _write(self, target: bytearray, chunk: bytes) -> None:
        if not isinstance(chunk, bytes):
            raise SandboxExecutionError("backend output chunks must be bytes")

        with self._lock:
            if len(target) + len(chunk) > self._limit:
                self._exceeded = True
                raise SandboxExecutionError(
                    "backend exceeded the configured output limit while streaming"
                )
            target.extend(chunk)


class SandboxBackend(Protocol):
    """OS-specific backend. Implementations must enforce, not merely simulate."""

    def probe(self, policy: object) -> CapabilityReport:
        """Return controls proven available for this exact host and policy."""
        ...

    def execute(
        self,
        request: SandboxRequest,
        policy: object,
        output: SandboxOutputCollector,
    ) -> SandboxResult:
        """Stream stdout/stderr to output while the process is running.

        Returned SandboxResult stdout/stderr must remain empty. Output must
        never be buffered without bounds and returned only after completion.
        """
        ...


class SandboxUnavailableError(RuntimeError):
    """Raised when required isolation cannot be proven."""


class SandboxExecutionError(RuntimeError):
    """Raised when backend output violates the declared execution contract."""
