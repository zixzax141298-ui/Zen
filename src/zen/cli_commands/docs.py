from zen.cli_core import CLIContext, Command, CommandRegistry

from .operations import CLIOperations


def register(registry: CommandRegistry, operations: CLIOperations) -> None:
    registry.register(
        Command(
            "docs",
            lambda context, _args: operations.print_docs(output=context.stdout),
        )
    )
