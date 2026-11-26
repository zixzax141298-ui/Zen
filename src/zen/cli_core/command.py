from __future__ import annotations

from argparse import Namespace
from dataclasses import dataclass, field
from typing import Callable

from .context import CLIContext


CommandHandler = Callable[[CLIContext, Namespace], int]


@dataclass(frozen=True, slots=True)
class Command:
    """A named CLI operation and the aliases that resolve to it."""

    name: str
    handler: CommandHandler
    aliases: tuple[str, ...] = field(default_factory=tuple)
    help: str = ""

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise ValueError("command name must be a non-empty trimmed string")
        if any(not alias or alias.strip() != alias for alias in self.aliases):
            raise ValueError("command aliases must be non-empty trimmed strings")
        if len(set(self.aliases)) != len(self.aliases) or self.name in self.aliases:
            raise ValueError("command aliases must be unique and differ from the name")
