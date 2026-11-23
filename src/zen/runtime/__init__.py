"""Zen language runtime / tree-walk interpreter.

Evaluates a semantically admissible program. Evaluation rules that remain
open questions (ZSS-04 OQ-07) are not invented; unsupported operations
raise RuntimeError with an explicit message.
"""

from .interpreter import Interpreter, RuntimeError, interpret

__all__ = [
    "Interpreter",
    "RuntimeError",
    "interpret",
]
