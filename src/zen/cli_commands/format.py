from zen.cli_core import CLIContext, Command, CommandRegistry

from .operations import CLIOperations


def register(registry: CommandRegistry, operations: CLIOperations) -> None:
    registry.register(
        Command(
            "format",
            lambda context, args: operations.format_source(
                args.file,
                output=context.stdout,
                error=context.stderr,
            ),
            aliases=("fmt",),
        )
    )
