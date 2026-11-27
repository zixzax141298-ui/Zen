from zen.cli_core import Command, CommandRegistry

from .operations import CLIOperations


def register(registry: CommandRegistry, operations: CLIOperations) -> None:
    # Register shell completion generation as a normal CLI command.
    registry.register(
        Command(
            "completion",
            lambda context, args: operations.generate_completion(
                args.shell,
                output=context.stdout,
                error=context.stderr,
            ),
        )
    )
