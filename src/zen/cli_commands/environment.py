from zen.cli_core import CLIContext, Command, CommandRegistry

from .operations import CLIOperations


def register(registry: CommandRegistry, operations: CLIOperations) -> None:
    registry.register(
        Command(
            "env",
            lambda context, _args: operations.print_environment(context.stdout),
        )
    )
    registry.register(
        Command(
            "version",
            lambda context, _args: operations.print_version(context.stdout),
        )
    )
    registry.register(
        Command(
            "doctor",
            lambda context, _args: operations.print_doctor(context.stdout),
        )
    )
    registry.register(
        Command(
            "info",
            lambda context, _args: operations.print_environment(context.stdout),
        )
    )
