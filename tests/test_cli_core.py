from argparse import Namespace
from io import StringIO

import pytest

from zen.cli_core import CLIContext, Command, CommandRegistry, ExitCode, dispatch


def test_registry_resolves_canonical_name_and_alias():
    registry = CommandRegistry()
    handler = lambda _context, _args: 7
    registry.register(Command("format", handler, aliases=("fmt",)))
    assert registry.resolve("format").name == "format"
    assert registry.resolve("fmt").name == "format"
    assert registry.resolve("missing") is None
    assert len(registry) == 1


def test_registry_rejects_duplicate_names_and_aliases():
    registry = CommandRegistry()
    registry.register(Command("format", lambda _c, _a: 0, aliases=("fmt",)))
    with pytest.raises(ValueError, match="already registered"):
        registry.register(Command("fmt", lambda _c, _a: 0))
    with pytest.raises(ValueError, match="already registered"):
        registry.register(Command("other", lambda _c, _a: 0, aliases=("fmt",)))


def test_command_rejects_invalid_aliases():
    with pytest.raises(ValueError):
        Command("run", lambda _c, _a: 0, aliases=("",))
    with pytest.raises(ValueError):
        Command("run", lambda _c, _a: 0, aliases=("run",))


def test_dispatch_invokes_registered_command_and_returns_integer():
    output = StringIO()
    registry = CommandRegistry()
    registry.register(Command("demo", lambda _c, _a: ExitCode.OK))
    result = dispatch(registry, CLIContext(stdout=output, stderr=output), "demo", Namespace())
    assert result == 0
    assert isinstance(result, int)


def test_dispatch_uses_default_only_when_command_is_absent():
    registry = CommandRegistry()
    context = CLIContext(stdout=StringIO(), stderr=StringIO())
    default = lambda _context, _args: 9
    assert dispatch(registry, context, None, Namespace(), default=default) == 9
    assert dispatch(registry, context, "unknown", Namespace(), default=default) == 2
