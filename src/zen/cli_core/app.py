from __future__ import annotations

from argparse import Namespace
from collections.abc import Callable

from .context import CLIContext
from .registry import CommandRegistry


DefaultHandler = Callable[[CLIContext, Namespace], int]


def dispatch(
    registry: CommandRegistry,
    context: CLIContext,
    command_name: str | None,
    args: Namespace,
    *,
    default: DefaultHandler | None = None,
    unknown_exit_code: int = 2,
) -> int:
    """Dispatch a parsed command; optionally route an absent command to default."""
    command = registry.resolve(command_name)
    if command is not None:
        return int(command.handler(context, args))
    if command_name is None and default is not None:
        return int(default(context, args))
    return int(unknown_exit_code)
