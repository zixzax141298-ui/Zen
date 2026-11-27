from argparse import ArgumentParser
from pathlib import Path

import pytest

from zen.cli_core.completion import (
    render_bash_completion,
    render_completion,
    render_zsh_completion,
)


def make_parser():
    parser = ArgumentParser(prog="zen")
    parser.add_argument("--no-color", action="store_true")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run")
    run.add_argument("file", type=Path)
    run.add_argument("--check", action="store_true")
    run.add_argument("--timeout", type=float)

    fmt = sub.add_parser("format", aliases=["fmt"])
    fmt.add_argument("file", type=Path)

    comp = sub.add_parser("completion")
    comp.add_argument("shell", choices=("bash", "zsh"))
    return parser


def test_bash_introspects_commands_aliases_global_and_command_options():
    script = render_bash_completion(make_parser())
    for value in ("run", "format", "fmt", "completion", "--no-color", "--check", "--timeout"):
        assert value in script


def test_bash_tracks_positional_choices_and_path_arguments():
    script = render_bash_completion(make_parser())
    assert "pos_kinds" in script
    assert "bash,zsh" in script
    assert "zenfiles" in script


def test_bash_supports_global_options_before_command():
    script = render_bash_completion(make_parser())
    assert "--no-color" in script
    assert "command_index" in script


def test_zsh_handles_global_options_and_discovers_command_position():
    script = render_zsh_completion(make_parser())
    assert "--no-color" in script
    assert "for ((i=1; i<CURRENT; i++))" in script
    assert 'case "$command" in' in script


def test_zsh_includes_aliases_positional_choices_and_typed_options():
    script = render_zsh_completion(make_parser())
    assert "fmt)" in script
    assert "format)" in script
    assert ":shell:(bash zsh)" in script
    assert "--timeout" in script


def test_unsupported_shell_rejected():
    with pytest.raises(ValueError, match="unsupported shell"):
        render_completion("fish", make_parser())


def test_bash_generator_does_not_depend_on_positional_parameters():
    script = render_bash_completion(make_parser())

    assert 'local cur="" word cmd=' in script
    assert 'local cur="$2"' not in script
    assert 'cur="${COMP_WORDS[COMP_CWORD]}"' in script


def test_bash_runtime_smoke_for_commands_choices_and_options():
    import shutil
    import subprocess
    from pathlib import Path as FilePath

    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash is not installed")

    script = render_bash_completion(make_parser())
    runner = f'''{script}
run_case() {{
    COMP_WORDS=("$@"); COMP_CWORD=$((${{#COMP_WORDS[@]}}-1));
    _zen_complete; printf '%s\\n' "${{COMPREPLY[*]}}";
}}
run_case zen ''
run_case zen completion ''
run_case zen completion b
run_case zen run --t
run_case zen --no-color ''
'''
    result = subprocess.run(
        [bash, "--noprofile", "--norc", "-c", runner],
        check=True, capture_output=True, text=True,
    )
    lines = result.stdout.splitlines()
    assert "run" in lines[0] and "completion" in lines[0]
    assert lines[1].split() == ["bash", "zsh"]
    assert lines[2] == "bash"
    assert "--timeout" in lines[3]
    assert "run" in lines[4]



def test_zsh_quotes_help_text_and_uses_zen_glob():
    import shutil
    import subprocess

    parser = ArgumentParser(prog="zen")
    parser.add_argument(
        "--version",
        action="store_true",
        help="show program's version number and exit",
    )
    sub = parser.add_subparsers(dest="command")
    run = sub.add_parser("run")
    run.add_argument("file", type=Path)

    script = render_zsh_completion(parser)

    # Apostrophes in argparse help must survive shell quoting.
    assert """program'"'"'s version""" in script

    # Path completion must use a real Zsh glob, without backslashes.
    assert ':file:_files -g "*.zen"' in script
    assert "shift words" not in script
    assert "CURRENT--" not in script
    assert r"\\*.zen" not in script

    zsh = shutil.which("zsh")
    if zsh is not None:
        result = subprocess.run(
            [zsh, "-n"],
            input=script,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr


def test_zsh_quotes_command_option_specs():
    parser = ArgumentParser(prog="zen")
    sub = parser.add_subparsers(dest="command")
    run = sub.add_parser("run")
    run.add_argument(
        "--message",
        help="display user's message",
    )

    script = render_zsh_completion(parser)

    # The complete _arguments specification must be shell-quoted.
    expected = "display user" + "'" + '"' + "'" + '"' + "'" + "s message"
    assert expected in script

def test_zsh_runtime_dispatch_and_generated_specs():
    import shutil
    import subprocess

    zsh = shutil.which("zsh")
    if zsh is None:
        pytest.skip("zsh is not installed")

    script = render_zsh_completion(make_parser())

    runner = r"""
set -eu
compdef() { :; }

_arguments() {
    if (( ARG_CALLS == 0 )); then
        state="$TEST_STATE"
    else
        print -r -- "ARG_SPEC:$*"
        print -r -- "ARG_CONTEXT:${(j:|:)words}:$CURRENT"
    fi
    (( ARG_CALLS += 1 ))
}

_describe() {
    print -r -- "DESCRIBE:$1"
    print -r -- "${command_specs[@]}"
}

_files() {
    print -r -- "FILES"
}

SCRIPT_UNDER_TEST

TEST_STATE=command
ARG_CALLS=0
words=(zen f)
CURRENT=2
print -r -- "---COMMANDS---"
_zen_completion

TEST_STATE=argument
ARG_CALLS=0
words=(zen run "")
CURRENT=3
print -r -- "---RUN_ARGUMENTS---"
_zen_completion

TEST_STATE=argument
ARG_CALLS=0
words=(zen completion b)
CURRENT=3
print -r -- "---CHOICES---"
_zen_completion
"""

    runner = runner.replace("SCRIPT_UNDER_TEST", script)

    result = subprocess.run(
        [zsh, "-f"],
        input=runner,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    output = result.stdout

    commands = output.split("---COMMANDS---", 1)[1].split(
        "---RUN_ARGUMENTS---", 1
    )[0]
    run_arguments = output.split("---RUN_ARGUMENTS---", 1)[1].split(
        "---CHOICES---", 1
    )[0]
    choices = output.split("---CHOICES---", 1)[1]

    for command in ("run", "format", "fmt", "completion"):
        assert command in commands

    assert "--check" in run_arguments
    assert "--timeout" in run_arguments
    assert "ARG_CONTEXT:zen|run|:3" in run_arguments
    assert ':file:_files -g "*.zen"' in run_arguments
    assert 'file:file:_files -g "*.zen"' not in run_arguments
    assert ":shell:(bash zsh)" in choices



def test_zsh_dispatch_starts_at_first_argument_after_arguments_context():
    script = render_zsh_completion(make_parser())

    # _arguments -C establishes a command-relative words array. The first
    # command candidate is therefore words[1], not words[2].
    assert "for ((i=1; i<CURRENT; i++))" in script
    assert 'run) command="${words[i]}"; break ;;' in script
    assert 'check) command="${words[i]}"; break ;;' not in script


def test_zsh_runtime_dispatch_uses_command_relative_words():
    import shutil
    import subprocess

    zsh = shutil.which("zsh")
    if zsh is None:
        pytest.skip("zsh is not installed")

    script = render_zsh_completion(make_parser())
    runner = r"""
set -eu
compdef() { :; }
ARG_CALLS=0
_arguments() {
    (( ARG_CALLS += 1 ))
    if (( ARG_CALLS == 1 )); then
        state=argument
        words=(run --che)
        CURRENT=2
    else
        print -r -- "$*"
    fi
}
_describe() { :; }
_files() { print -r -- "FILES"; }

SCRIPT_UNDER_TEST
_zen_completion
"""
    result = subprocess.run(
        [zsh, "-f"],
        input=runner.replace("SCRIPT_UNDER_TEST", script),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "--check" in result.stdout
    assert "FILES" not in result.stdout


def test_bash_global_value_matching_command_does_not_shift_position(tmp_path):
    import shutil
    import subprocess

    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash is not installed")

    parser = ArgumentParser(prog="zen")
    parser.add_argument("--profile", type=str)
    sub = parser.add_subparsers(dest="command")
    run = sub.add_parser("run")
    run.add_argument("file", type=Path)

    (tmp_path / "alpha.zen").write_text("")
    (tmp_path / "notes.txt").write_text("")

    script = render_bash_completion(parser) + r'''
COMP_WORDS=(zen --profile run run "")
COMP_CWORD=4
_zen_complete
printf '%s\n' "${COMPREPLY[@]}"
'''

    result = subprocess.run(
        [bash, "--noprofile", "--norc", "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    candidates = result.stdout.splitlines()
    assert candidates
    assert all(candidate.endswith(".zen") for candidate in candidates)


def test_bash_filename_completion_preserves_spaces(tmp_path):
    import shutil
    import subprocess

    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash is not installed")

    parser = make_parser()
    (tmp_path / "my project.zen").write_text("")
    (tmp_path / "other.zen").write_text("")

    script = render_bash_completion(parser) + r'''
COMP_WORDS=(zen run "")
COMP_CWORD=2
_zen_complete
printf '%s\n' "${COMPREPLY[@]}"
'''

    result = subprocess.run(
        [bash, "--noprofile", "--norc", "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    candidates = result.stdout.splitlines()
    assert any(
        Path(candidate).name == "my project.zen"
        for candidate in candidates
    )


def test_bash_completes_choice_option_with_equals(tmp_path):
    import shutil
    import subprocess

    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash is not installed")

    parser = ArgumentParser(prog="zen")
    sub = parser.add_subparsers(dest="command")
    run = sub.add_parser("run")
    run.add_argument("file", type=Path)
    run.add_argument("--profile", choices=("dev", "prod"))

    script = render_bash_completion(parser) + r'''
COMP_WORDS=(zen run --profile=)
COMP_CWORD=2
_zen_complete
printf '%s\n' "${COMPREPLY[@]}"
'''

    result = subprocess.run(
        [bash, "--noprofile", "--norc", "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert set(result.stdout.splitlines()) == {
        "--profile=dev",
        "--profile=prod",
    }


def test_bash_repeats_path_completion_for_positional_plus(tmp_path):
    import shutil
    import subprocess

    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash is not installed")

    parser = ArgumentParser(prog="zen")
    sub = parser.add_subparsers(dest="command")
    run = sub.add_parser("run")
    run.add_argument("files", nargs="+", type=Path)

    (tmp_path / "first.zen").write_text("")
    (tmp_path / "second.zen").write_text("")
    (tmp_path / "notes.txt").write_text("")

    script = render_bash_completion(parser) + r'''
COMP_WORDS=(zen run first.zen s)
COMP_CWORD=3
_zen_complete
printf '%s\n' "${COMPREPLY[@]}"
'''

    result = subprocess.run(
        [bash, "--noprofile", "--norc", "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    candidates = result.stdout.splitlines()
    assert candidates
    assert all(candidate.endswith(".zen") for candidate in candidates)
    assert "notes.txt" not in candidates


def test_bash_completes_global_choice_option_with_equals(tmp_path):
    import shutil
    import subprocess

    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash is not installed")

    parser = ArgumentParser(prog="zen")
    parser.add_argument("--profile", choices=("dev", "prod"))
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run")

    script = render_bash_completion(parser) + r'''
COMP_WORDS=(zen --profile= run)
COMP_CWORD=1
_zen_complete
printf '%s\n' "${COMPREPLY[@]}"
'''

    result = subprocess.run(
        [bash, "--noprofile", "--norc", "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert set(result.stdout.splitlines()) == {
        "--profile=dev",
        "--profile=prod",
    }


def test_zsh_skips_global_option_values_when_finding_command():
    import shutil
    import subprocess

    zsh = shutil.which("zsh")
    if zsh is None:
        pytest.skip("zsh is not installed")

    parser = ArgumentParser(prog="zen")
    parser.add_argument("--profile", choices=("format", "prod"))
    sub = parser.add_subparsers(dest="command")

    format_parser = sub.add_parser("format")
    format_parser.add_argument("--format-only", action="store_true")

    run_parser = sub.add_parser("run")
    run_parser.add_argument("--run-only", action="store_true")

    script = render_zsh_completion(parser)

    runner = r"""
set -eu
compdef() { :; }

_arguments() {
    if (( ARG_CALLS == 0 )); then
        state=argument
    else
        print -r -- "ARG_SPEC:$*"
    fi
    (( ARG_CALLS += 1 ))
}

_describe() { :; }
_files() { :; }

SCRIPT_UNDER_TEST

ARG_CALLS=0
words=(zen --profile format run "")
CURRENT=5
_zen_completion
"""

    result = subprocess.run(
        [zsh, "-f"],
        input=runner.replace("SCRIPT_UNDER_TEST", script),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "--run-only" in result.stdout
    assert "--format-only" not in result.stdout


def test_zsh_skips_equals_form_global_option_value_when_finding_command():
    import shutil
    import subprocess

    zsh = shutil.which("zsh")
    if zsh is None:
        pytest.skip("zsh is not installed")

    parser = ArgumentParser(prog="zen")
    parser.add_argument("--profile", choices=("format", "prod"))
    sub = parser.add_subparsers(dest="command")

    format_parser = sub.add_parser("format")
    format_parser.add_argument("--format-only", action="store_true")

    run_parser = sub.add_parser("run")
    run_parser.add_argument("--run-only", action="store_true")

    script = render_zsh_completion(parser)
    runner = r"""
set -eu
compdef() { :; }
_arguments() {
    if (( ARG_CALLS == 0 )); then
        state=argument
    else
        print -r -- "ARG_SPEC:$*"
    fi
    (( ARG_CALLS += 1 ))
}
_describe() { :; }
_files() { :; }

SCRIPT_UNDER_TEST

ARG_CALLS=0
words=(zen --profile=format run "")
CURRENT=4
_zen_completion
"""

    result = subprocess.run(
        [zsh, "-f"],
        input=runner.replace("SCRIPT_UNDER_TEST", script),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "--run-only" in result.stdout
    assert "--format-only" not in result.stdout
