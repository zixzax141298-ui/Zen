from __future__ import annotations

import shutil
import subprocess

import pytest

from zen.cli import main


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_completion_command_writes_script_to_stdout(shell, capsys):
    assert main(["completion", shell]) == 0
    captured = capsys.readouterr()

    assert captured.out
    assert captured.err == ""
    if shell == "bash":
        assert "# Bash completion for zen; generated from argparse metadata." in captured.out
        assert "complete -F" in captured.out
    else:
        assert captured.out.startswith("#compdef zen")
        assert "compdef" in captured.out


def test_completion_command_rejects_unsupported_shell(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["completion", "fish"])

    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "invalid choice" in captured.err
    assert "bash" in captured.err
    assert "zsh" in captured.err


@pytest.mark.parametrize(("shell", "executable"), [("bash", "bash"), ("zsh", "zsh")])
def test_generated_completion_script_has_valid_shell_syntax(shell, executable):
    binary = shutil.which(executable)
    if binary is None:
        pytest.skip(f"{executable} is not installed")

    from zen.cli import _argument_parser
    from zen.cli_core.completion import render_completion

    script = render_completion(shell, _argument_parser())
    result = subprocess.run(
        [binary, "-n"], input=script, text=True, capture_output=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_completion_output_write_failure_returns_io_error(monkeypatch):
    import io
    import sys

    class BrokenOutput:
        def write(self, _value):
            raise OSError("simulated output failure")

        def flush(self):
            raise OSError("simulated output failure")

    error = io.StringIO()
    monkeypatch.setattr(sys, "stdout", BrokenOutput())
    monkeypatch.setattr(sys, "stderr", error)

    assert main(["completion", "bash"]) == 1
    assert "cannot write completion output" in error.getvalue()
