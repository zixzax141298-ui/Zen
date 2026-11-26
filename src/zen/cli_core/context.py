from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import TextIO


@dataclass(frozen=True, slots=True)
class CLIContext:
    """Per-invocation streams and program metadata for CLI commands."""

    stdout: TextIO = field(default_factory=lambda: sys.stdout)
    stderr: TextIO = field(default_factory=lambda: sys.stderr)
    program_name: str = "zen"
