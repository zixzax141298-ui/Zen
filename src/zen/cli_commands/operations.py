from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class CLIOperations:
    """Application operations supplied by the CLI entrypoint."""

    run_file: Callable[..., int]
    dump_ast: Callable[..., int]
    dump_tokens: Callable[..., int]
    fingerprint_file: Callable[..., int]
    format_source: Callable[..., int]
    print_docs: Callable[..., int]
    run_repl: Callable[..., int]
    print_environment: Callable[..., int]
    print_version: Callable[..., int]
    print_doctor: Callable[..., int]
    generate_completion: Callable[..., int]
    install_completion: Callable[..., int]
    uninstall_completion: Callable[..., int]
