"""Immutable policy for ZEAI sandbox workloads."""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SandboxPolicy:
    """Declarative limits; this policy does not itself provide OS isolation."""

    workspace_root: Path
    timeout_seconds: float = 10.0
    max_memory_bytes: int = 256 * 1024 * 1024
    max_cpu_seconds: int = 10
    max_output_bytes: int = 1024 * 1024
    allowed_environment: frozenset[str] = field(default_factory=frozenset)
    network_enabled: bool = False

    def __post_init__(self) -> None:
        root = Path(self.workspace_root).expanduser().resolve()
        object.__setattr__(self, "workspace_root", root)

        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        if self.max_memory_bytes <= 0 or self.max_cpu_seconds <= 0:
            raise ValueError("resource limits must be greater than zero")
        if self.max_output_bytes <= 0:
            raise ValueError("max_output_bytes must be greater than zero")
        if self.network_enabled:
            raise ValueError(
                "network access is prohibited by the current sandbox contract"
            )
        if any(not name.isidentifier() for name in self.allowed_environment):
            raise ValueError("environment allowlist contains an invalid variable name")

    def contains_path(self, path: Path) -> bool:
        """Return true only when the resolved path remains inside workspace_root."""
        try:
            Path(path).expanduser().resolve().relative_to(self.workspace_root)
            return True
        except (OSError, ValueError):
            return False
