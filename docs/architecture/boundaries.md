# Architecture boundaries

This document defines ownership boundaries between Zen language components.
It does not imply that components marked as future work are implemented.

## AST boundaries

- **Lexer owns lexical validity.** It validates characters, token forms,
  literals, identifiers, comments, and lexical resource limits. AST code must
  not import or depend on lexer implementation details or lexer limits.
- **Parser owns grammar validity, resource limits, and diagnostics.** It
  consumes tokens, constructs AST nodes, enforces AST node/depth limits, and
  reports source-located diagnostics. The v0.1 grammar parser is implemented in `src/zen/parser`.
- **AST owns structural invariants.** AST nodes are immutable canonical data
  structures. They validate child types, child-span containment, direct
  collection bounds, and source-ordered non-overlapping siblings. Explicit
  validation utilities detect cycles and reused node identities when requested.
- **Semantic analysis owns semantic validity.** Name resolution, type checking,
  constant assignment rules, and callable checks belong to semantic analysis,
  not the AST model.
- **IR owns canonical representation and transformations.** A future
  intermediate representation layer will define canonical compiler-facing
  representation and controlled transformations. It must not be used to hide
  invalid AST structure.

## Source spans

Source spans are half-open: start is inclusive and end is exclusive. A child
must be contained by its parent. Siblings are ordered and non-overlapping;
`previous.end == next.start` is valid adjacency.
