from __future__ import annotations

from .command import Command


class CommandRegistry:
    """Deterministic command/alias registry; duplicate names are rejected."""

    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}
        self._names: dict[str, str] = {}

    def register(self, command: Command) -> None:
        keys = (command.name, *command.aliases)
        collisions = [key for key in keys if key in self._names]
        if collisions:
            raise ValueError(f"command name or alias already registered: {collisions[0]}")
        self._commands[command.name] = command
        for key in keys:
            self._names[key] = command.name

    def resolve(self, name: str | None) -> Command | None:
        if name is None:
            return None
        canonical = self._names.get(name)
        return self._commands.get(canonical) if canonical is not None else None

    def __contains__(self, name: str) -> bool:
        return name in self._names

    def __len__(self) -> int:
        return len(self._commands)

    def commands(self) -> tuple[Command, ...]:
        return tuple(self._commands.values())
