from zen.cli_core import CommandRegistry

from . import docs, environment, format, inspect, repl, run
from .operations import CLIOperations


def register_commands(
    registry: CommandRegistry,
    operations: CLIOperations,
) -> CommandRegistry:
    """Register built-in commands using injected application operations."""
    run.register(registry, operations)
    inspect.register(registry, operations)
    format.register(registry, operations)
    docs.register(registry, operations)
    environment.register(registry, operations)
    repl.register(registry, operations)
    return registry


__all__ = ["CLIOperations", "register_commands"]
