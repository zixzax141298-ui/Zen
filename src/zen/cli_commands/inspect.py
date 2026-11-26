from zen.cli_core import CLIContext, Command, CommandRegistry

from .operations import CLIOperations


def register(registry: CommandRegistry, operations: CLIOperations) -> None:
    registry.register(
        Command(
            "ast",
            lambda context, args: operations.dump_ast(
                args.file,
                output=context.stdout,
                error=context.stderr,
            ),
        )
    )
    registry.register(
        Command(
            "fp",
            lambda context, args: operations.fingerprint_file(
                args.file,
                output=context.stdout,
                error=context.stderr,
            ),
        )
    )
    registry.register(
        Command(
            "tokens",
            lambda context, args: operations.dump_tokens(
                args.file,
                output=context.stdout,
                error=context.stderr,
            ),
        )
    )
