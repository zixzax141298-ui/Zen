"""Shell completion generation from an argparse parser.

The parser is the single source of truth for commands, aliases, options,
choices, and positional argument types. No command names are maintained here.
"""
from __future__ import annotations

import argparse
import shlex
from pathlib import Path
from typing import Any


def _subparser_action(parser: argparse.ArgumentParser) -> argparse._SubParsersAction | None:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action
    return None


def _actions(parser: argparse.ArgumentParser) -> list[argparse.Action]:
    return [a for a in parser._actions if a.option_strings and a.dest != "help"]


def _positionals(parser: argparse.ArgumentParser) -> list[argparse.Action]:
    return [a for a in parser._actions if not a.option_strings and a.dest != "help"]


def _takes_value(action: argparse.Action) -> bool:
    return action.nargs != 0 and not isinstance(
        action, (argparse._StoreTrueAction, argparse._StoreFalseAction,
                 argparse._CountAction, argparse._HelpAction, argparse._VersionAction)
    )


def _choices(action: argparse.Action) -> list[str]:
    return [str(v) for v in action.choices] if action.choices is not None else []


def _kind(action: argparse.Action) -> str:
    if _choices(action):
        return "choices"
    if action.type is Path:
        return "zenfiles"
    if action.type in (int, float):
        return "number"
    return "files"


def _metadata(parser: argparse.ArgumentParser) -> dict[str, Any]:
    sub = _subparser_action(parser)
    commands: list[str] = []
    canonical: dict[str, str] = {}
    parsers: dict[str, argparse.ArgumentParser] = {}
    if sub is not None:
        for name, child in sub.choices.items():
            commands.append(name)
            root = next((n for n, p in sub.choices.items() if p is child and n not in canonical), name)
            canonical[name] = root
            parsers.setdefault(root, child)
    return {
        "program": parser.prog.split()[-1],
        "commands": commands,
        "canonical": canonical,
        "parsers": parsers,
        "global_options": _actions(parser),
    }


def _bash_words(values: list[str]) -> str:
    return " ".join(shlex.quote(v) for v in values)


def render_bash_completion(parser: argparse.ArgumentParser) -> str:
    """Render Bash completion with command-, option-, and position-aware logic."""
    m = _metadata(parser)
    program = m["program"]
    func = "_" + program.replace("-", "_") + "_complete"
    commands = _bash_words(m["commands"])
    global_opts = _bash_words([o for a in m["global_options"] for o in a.option_strings])
    global_values = _bash_words([o for a in m["global_options"] if _takes_value(a) for o in a.option_strings])

    command_cases: list[str] = []
    value_completion_cases: list[str] = []
    equals_completion_cases: list[str] = []
    global_equals_completion_cases: list[str] = []
    for alias, canonical in m["canonical"].items():
        child = m["parsers"][canonical]
        opts = _bash_words([o for a in _actions(child) for o in a.option_strings])
        value_actions = [a for a in _actions(child) if _takes_value(a)]
        value_opts = _bash_words([o for a in value_actions for o in a.option_strings])
        value_cases = []
        for action in value_actions:
            for option in action.option_strings:
                choices_for_option = _choices(action)
                if choices_for_option:
                    equals_completion_cases.append(
                        f"        {shlex.quote(alias + ':' + option)}) "
                        'COMPREPLY=(); while IFS= read -r candidate; do '
                        'COMPREPLY+=("${cur%%=*}=${candidate}"); done '
                        f'< <(compgen -W {shlex.quote(_bash_words(choices_for_option))} -- "${{cur#*=}}"); '
                        'return 0 ;;'
                    )
                elif action.type is Path:
                    equals_completion_cases.append(
                        f"        {shlex.quote(alias + ':' + option)}) "
                        'COMPREPLY=(); while IFS= read -r candidate; do '
                        '[[ "$candidate" == *.zen ]] && '
                        'COMPREPLY+=("${cur%%=*}=${candidate}"); done '
                        '< <(compgen -f -- "${cur#*=}"); return 0 ;;'
                    )
                else:
                    equals_completion_cases.append(
                        f"        {shlex.quote(alias + ':' + option)}) "
                        'COMPREPLY=(); return 0 ;;'
                    )
                if choices_for_option:
                    value_completion_cases.append(f"        {shlex.quote(alias + ':' + option)}) COMPREPLY=( $(compgen -W {shlex.quote(_bash_words(choices_for_option))} -- \"$cur\") ); return 0 ;;")
                elif action.type is Path:
                    value_completion_cases.append(
                        f"        {shlex.quote(alias + ':' + option)}) "
                        'COMPREPLY=(); while IFS= read -r candidate; do '
                        'COMPREPLY+=("$candidate"); done '
                        '< <(compgen -f -- "$cur"); '
                        'local filtered=() item; '
                        'for item in "${COMPREPLY[@]}"; do '
                        '[[ "$item" == *.zen ]] && filtered+=("$item"); '
                        'done; COMPREPLY=("${filtered[@]}"); return 0 ;;'
                    )
                else:
                    value_completion_cases.append(f"        {shlex.quote(alias + ':' + option)}) COMPREPLY=(); return 0 ;;")
        positional = _positionals(child)
        kinds = _bash_words([_kind(a) for a in positional])
        choices = "|".join(",".join(_choices(a)) for a in positional)
        command_cases.append(
            f"        {shlex.quote(alias)}) opts={shlex.quote(opts)}; value_opts={shlex.quote(value_opts)}; "
            f"pos_kinds={shlex.quote(kinds)}; pos_choices={shlex.quote(choices)} ;;"
        )

    # Global options may occur before or after the command.
    for action in m["global_options"]:
        if not _takes_value(action):
            continue
        for option in action.option_strings:
            choices_for_option = _choices(action)
            if choices_for_option:
                global_equals_completion_cases.append(
                    f"        *:{shlex.quote(option)}) "
                    'COMPREPLY=(); while IFS= read -r candidate; do '
                    'COMPREPLY+=("${cur%%=*}=${candidate}"); done '
                    f'< <(compgen -W {shlex.quote(_bash_words(choices_for_option))} -- "${{cur#*=}}"); '
                    'return 0 ;;'
                )
            elif action.type is Path:
                global_equals_completion_cases.append(
                    f"        *:{shlex.quote(option)}) "
                    'COMPREPLY=(); while IFS= read -r candidate; do '
                    '[[ "$candidate" == *.zen ]] && '
                    'COMPREPLY+=("${cur%%=*}=${candidate}"); done '
                    '< <(compgen -f -- "${cur#*=}"); return 0 ;;'
                )
            else:
                global_equals_completion_cases.append(
                    f"        *:{shlex.quote(option)}) "
                    'COMPREPLY=(); return 0 ;;'
                )

    return f'''# Bash completion for {program}; generated from argparse metadata.
{func}() {{
    local cur="" word cmd="" previous="" opts="" value_opts="" pos_kinds="" pos_choices=""
    local candidate
    local i j command_index=-1 positional_index=0 kind choice_list
    local -a words choices_array
    words=("${{COMP_WORDS[@]}}")
    cur="${{COMP_WORDS[COMP_CWORD]}}"

    # Complete global values embedded in --option=value tokens.
    if [[ "$cur" == *=* ]]; then
        case "$cmd:${{cur%%=*}}" in
{chr(10).join(global_equals_completion_cases)}
            *) ;;
        esac
    fi

    # Find the command, skipping global options and their values.
    for ((i=1; i<COMP_CWORD; i++)); do
        word="${{words[i]}}"
        if [[ " {global_values} " == *" $word "* ]]; then ((i+=1)); continue; fi
        [[ "$word" == -* ]] && continue
        case " {commands} " in *" $word "*) cmd="$word"; break ;; esac
        break
    done

    if [[ -z "$cmd" ]]; then
        if [[ "$cur" == -* ]]; then COMPREPLY=( $(compgen -W "{global_opts}" -- "$cur") )
        else COMPREPLY=( $(compgen -W "{commands}" -- "$cur") ); fi
        return 0
    fi

    case "$cmd" in
{chr(10).join(command_cases)}
        *) opts=""; value_opts=""; pos_kinds=""; pos_choices="" ;;
    esac

    # Complete command-specific values embedded in --option=value tokens.
    if [[ "$cur" == *=* ]]; then
        case "$cmd:${{cur%%=*}}" in
{chr(10).join(equals_completion_cases)}
            *) ;;
        esac
    fi

    # Count positional arguments before the cursor; option values are not positional.
    positional_index=0
    for ((i=command_index_placeholder; i<COMP_CWORD; i++)); do :; done
    # Locate command index and walk command arguments.
    for ((i=1; i<COMP_CWORD; i++)); do
        [[ "${{words[i]}}" == "$cmd" ]] && {{ command_index=$i; break; }}
    done
    for ((i=command_index+1; i<COMP_CWORD; i++)); do
        word="${{words[i]}}"
        if [[ " $value_opts " == *" $word "* ]]; then ((i+=1)); continue; fi
        [[ "$word" == -* ]] && continue
        ((positional_index+=1))
    done

    previous=""
    (( COMP_CWORD > 1 )) && previous="${{words[COMP_CWORD-1]}}"

    if [[ " $value_opts " == *" $previous "* ]]; then
        case "$cmd:$previous" in
{chr(10).join(value_completion_cases)}
            *) COMPREPLY=(); return 0 ;;
        esac
    fi
    if [[ "$cur" == -* ]]; then COMPREPLY=( $(compgen -W "$opts" -- "$cur") ); return 0; fi

    kind="$(printf '%s\\n' "$pos_kinds" | cut -d' ' -f$((positional_index+1)))"
    choice_list="$(printf '%s\\n' "$pos_choices" | cut -d'|' -f$((positional_index+1)))"
    if [[ "$kind" == choices && -n "$choice_list" ]]; then
        COMPREPLY=( $(compgen -W "${{choice_list//,/ }}" -- "$cur") )
    elif [[ "$kind" == zenfiles ]]; then
        COMPREPLY=()
        while IFS= read -r candidate; do
            [[ "$candidate" == *.zen ]] && COMPREPLY+=("$candidate")
        done < <(compgen -f -- "$cur")
    else
        COMPREPLY=()
        while IFS= read -r candidate; do
            COMPREPLY+=("$candidate")
        done < <(compgen -f -- "$cur")
    fi
    return 0
}}
complete -F {func} {shlex.quote(program)}
'''.replace("    for ((i=command_index_placeholder; i<COMP_CWORD; i++)); do :; done\n", "")


def render_zsh_completion(parser: argparse.ArgumentParser) -> str:
    """Render a Zsh completion function that handles global options before commands."""
    m = _metadata(parser)
    program = m["program"]
    func = "_" + program.replace("-", "_") + "_completion"
    command_specs = [f"{name}:{name} command" for name in m["commands"]]

    command_cases: list[str] = []
    for alias, canonical in m["canonical"].items():
        child = m["parsers"][canonical]
        specs: list[str] = []
        for action in _actions(child):
            for option in action.option_strings:
                help_text = (action.help or "option").replace("[", "").replace("]", "")
                if _takes_value(action):
                    if _choices(action):
                        vals = " ".join(shlex.quote(value) for value in _choices(action))
                        specs.append(f"{option}[{help_text}]:value:({vals})")
                    elif action.type is Path:
                        specs.append(f"{option}[{help_text}]:file:_files -g \"*.zen\"")
                    else:
                        specs.append(f"{option}[{help_text}]:value:")
                else:
                    specs.append(f"{option}[{help_text}]")
        for action in _positionals(child):
            choices = _choices(action)
            if choices:
                vals = " ".join(shlex.quote(v) for v in choices)
                specs.append(f":{action.help or action.dest}:({vals})")
            elif action.type is Path:
                specs.append(f":{action.help or action.dest}:_files -g \"*.zen\"")
            else:
                specs.append(f"{action.dest}:value:")
        command_cases.append(
            f"        {shlex.quote(alias)}) _arguments "
            + " ".join(shlex.quote(spec) for spec in specs)
            + " ;;"
            if specs
            else f"        {shlex.quote(alias)}) _files ;;"
        )

    global_specs: list[str] = []
    for action in m["global_options"]:
        for option in action.option_strings:
            if _takes_value(action):
                global_specs.append(f"{option}[{action.help or 'option'}]:value:")
            else:
                global_specs.append(f"{option}[{action.help or 'option'}]")

    global_value_options = [
        option
        for action in m["global_options"]
        if _takes_value(action)
        for option in action.option_strings
    ]
    global_value_skip = ""
    if global_value_options:
        patterns = "|".join(
            shlex.quote(option) for option in global_value_options
        )
        equals_patterns = "|".join(
            shlex.quote(option + "=") + "*" for option in global_value_options
        )
        global_value_skip = f'''                case "${{words[i]}}" in
                    {patterns}) i=$((i + 1)); continue ;;
                    {equals_patterns}) continue ;;
                esac
'''

    return f'''#compdef {program}
# Generated from argparse metadata.
{func}() {{
    local state command="" i
    local -a command_specs
    _arguments -C \\
        {' '.join(shlex.quote(spec) for spec in global_specs)} \\
        '1:command:->command' \\
        '*::argument:->argument'
    case "$state" in
        command)
            command_specs=(
{chr(10).join('                ' + shlex.quote(s) for s in command_specs)}
            )
            _describe 'command' command_specs
            ;;
        argument)
            for ((i=1; i<CURRENT; i++)); do
{global_value_skip}                case "${{words[i]}}" in
{chr(10).join('                    ' + shlex.quote(n) + ') command="${words[i]}"; break ;;' for n in m["commands"])}
                esac
            done
            case "$command" in
{chr(10).join(command_cases)}
                *) _files ;;
            esac
            ;;
    esac
}}
compdef {func} {program}
'''


def render_completion(shell: str, parser: argparse.ArgumentParser) -> str:
    if shell == "bash":
        return render_bash_completion(parser)
    if shell == "zsh":
        return render_zsh_completion(parser)
    raise ValueError(f"unsupported shell: {shell}")
