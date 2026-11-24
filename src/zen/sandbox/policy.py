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
    max_stdin_bytes: int = 1024 * 1024
    max_argv_count: int = 128
    max_argv_item_bytes: int = 32 * 1024
    max_argv_total_bytes: int = 128 * 1024
    max_environment_count: int = 32
    max_environment_value_bytes: int = 8 * 1024
    max_environment_total_bytes: int = 32 * 1024
    allowed_environment: frozenset[str] = field(default_factory=frozenset)
    network_enabled: bool = False

    def __post_init__(self) -> None:
        root = Path(self.workspace_root).expanduser().resolve()
        object.__setattr__(self, "workspace_root", root)

        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        if self.max_memory_bytes <= 0 or self.max_cpu_seconds <= 0:
            raise ValueError("resource limits must be greater than zero")
        positive_limits = {
            "max_output_bytes": self.max_output_bytes,
            "max_stdin_bytes": self.max_stdin_bytes,
            "max_argv_count": self.max_argv_count,
            "max_argv_item_bytes": self.max_argv_item_bytes,
            "max_argv_total_bytes": self.max_argv_total_bytes,
            "max_environment_count": self.max_environment_count,
            "max_environment_value_bytes": self.max_environment_value_bytes,
            "max_environment_total_bytes": self.max_environment_total_bytes,
        }
        for name, value in positive_limits.items():
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
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
