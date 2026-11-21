"""Resource limits for Zen language structures.

MAX_AST_NODES is the maximum total number of AST nodes for one Program.
MAX_AST_DEPTH is the maximum structural nesting depth of an AST.
MAX_DIRECT_CHILDREN is the maximum number of direct children in one collection.
MAX_EXPRESSION_NODES is the maximum number of nodes in one expression tree.
MAX_STATEMENT_NODES is the maximum number of nodes in one statement tree.

Lexical resource limits belong to the lexer and are intentionally not exported
from this module.
"""

MAX_AST_NODES = 1_000_000
MAX_AST_DEPTH = 256
MAX_DIRECT_CHILDREN = 262_144
MAX_EXPRESSION_NODES = 262_144
MAX_STATEMENT_NODES = 262_144
