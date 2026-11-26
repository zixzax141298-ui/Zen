from zen.cli_core import CLIContext, Command, CommandRegistry

from .operations import CLIOperations


def register(registry: CommandRegistry, operations: CLIOperations) -> None:
    def run(context: CLIContext, args) -> int:
        return operations.run_file(
            args.file,
            output=context.stdout,
            error=context.stderr,
            check_only=args.check,
            json_output=args.json,
            show_stats=args.stats,
            timeout=args.timeout,
        )

    def check(context: CLIContext, args) -> int:
        return operations.run_file(
            args.file,
            output=context.stdout,
            error=context.stderr,
            check_only=True,
            json_output=args.json,
        )

    registry.register(Command("run", run))
    registry.register(Command("check", check))
