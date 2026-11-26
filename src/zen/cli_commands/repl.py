from zen.cli_core import CLIContext, Command, CommandRegistry

from .operations import CLIOperations


def register(registry: CommandRegistry, operations: CLIOperations) -> None:
    registry.register(
        Command(
            "repl",
            lambda context, _args: operations.run_repl(output=context.stdout),
        )
    )
