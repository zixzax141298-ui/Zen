"""Resource limits for Zen language structures.

MAX_AST_NODES is the maximum total number of AST nodes for one Program.
MAX_AST_DEPTH is the maximum structural nesting depth of an AST.
MAX_PARSER_DEPTH is the maximum parser nesting depth.
MAX_DIRECT_CHILDREN is the maximum number of direct children in one collection.
MAX_EXPRESSION_NODES is the maximum number of nodes in one expression tree.
MAX_STATEMENT_NODES is the maximum number of nodes in one statement tree.

Lexical resource limits belong to the lexer and are intentionally not exported
from this module.
"""

MAX_AST_NODES = 1_000_000
MAX_AST_DEPTH = 256

# A separate dimension with the same initial ceiling as the former
# shared parser/AST depth value. This does not increase or weaken the limit.
MAX_PARSER_DEPTH = 256

MAX_DIRECT_CHILDREN = 262_144
MAX_EXPRESSION_NODES = 262_144
MAX_STATEMENT_NODES = 262_144


# Runtime budget: approximately nine AST operations per simple loop iteration.
MAX_RUNTIME_STEPS = 50_000_000

# Keep Zen recursion comfortably below Python's own recursion limit.
MAX_CALL_DEPTH = 64
