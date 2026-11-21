"""Explicit structural validation utilities for AST trees and AST-like graphs."""

from .nodes import Node
from .traversal import iter_child_nodes


def require_child_span(parent: Node, child: Node, field_name: str) -> None:
    if not isinstance(parent, Node) or not isinstance(child, Node):
        raise TypeError("parent and child must be AST Nodes")
    if not parent.span.contains(child.span):
        raise ValueError(f"{field_name} span must be contained in parent span")


def require_ordered_children(parent: Node, children: tuple[Node, ...], field_name: str) -> None:
    if not isinstance(parent, Node):
        raise TypeError("parent must be an AST Node")
    previous = None
    for child in children:
        if not isinstance(child, Node):
            raise TypeError(f"{field_name} must contain only AST Nodes")
        require_child_span(parent, child, field_name)
        if previous is not None and child.span.start < previous.span.end:
            raise ValueError(f"{field_name} spans must be ordered and non-overlapping")
        previous = child


def detect_cycles(root: Node) -> None:
    """Raise ValueError if a depth-first traversal finds a graph cycle."""
    if not isinstance(root, Node):
        raise TypeError("root must be an AST Node")
    visiting: set[int] = set()
    visited: set[int] = set()
    stack = [(root, iter_child_nodes(root))]
    visiting.add(id(root))
    while stack:
        node, children = stack[-1]
        try:
            child = next(children)
        except StopIteration:
            stack.pop()
            visiting.remove(id(node))
            visited.add(id(node))
            continue
        child_id = id(child)
        if child_id in visiting:
            raise ValueError("AST cycle detected")
        if child_id not in visited:
            visiting.add(child_id)
            stack.append((child, iter_child_nodes(child)))


def detect_reused_nodes(root: Node) -> None:
    """Raise ValueError if a Node object occurs at more than one tree location."""
    if not isinstance(root, Node):
        raise TypeError("root must be an AST Node")
    seen = {id(root)}
    stack = [root]
    while stack:
        node = stack.pop()
        for child in iter_child_nodes(node):
            child_id = id(child)
            if child_id in seen:
                raise ValueError("AST node reuse detected")
            seen.add(child_id)
            stack.append(child)


def _unique_preorder(root: Node):
    if not isinstance(root, Node):
        raise TypeError("root must be an AST Node")
    seen = set()
    stack = [root]
    while stack:
        node = stack.pop()
        node_id = id(node)
        if node_id in seen:
            raise ValueError("AST graph is not a finite tree")
        seen.add(node_id)
        yield node
        stack.extend(reversed(tuple(iter_child_nodes(node))))


def count_nodes(root: Node) -> int:
    """Count all nodes in a finite tree, including its root."""
    return sum(1 for _ in _unique_preorder(root))


def measure_depth(root: Node) -> int:
    """Return maximum structural depth; the root has depth one."""
    if not isinstance(root, Node):
        raise TypeError("root must be an AST Node")
    maximum = 0
    seen = set()
    stack = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        if id(node) in seen:
            raise ValueError("AST graph is not a finite tree")
        seen.add(id(node))
        maximum = max(maximum, depth)
        stack.extend((child, depth + 1) for child in iter_child_nodes(node))
    return maximum
