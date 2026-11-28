from zen.cli_core import Command, CommandRegistry

from .operations import CLIOperations


def register(registry: CommandRegistry, operations: CLIOperations) -> None:
    def handle_completion(context, args) -> int:
        if args.install:
            return operations.install_completion(
                args.shell,
                output=context.stdout,
                error=context.stderr,
            )

        if args.uninstall:
            return operations.uninstall_completion(
                args.shell,
                output=context.stdout,
                error=context.stderr,
            )

        return operations.generate_completion(
            args.shell,
            output=context.stdout,
            error=context.stderr,
        )

    registry.register(Command("completion", handle_completion))
