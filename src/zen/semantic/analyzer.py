"""Semantic analyzer for Zen v0.1.

Implements only rules that are explicitly directed by the language
specification or approved design documents. Unresolved OQs from
ZSS-04 are *not* silently decided.

Implemented:
- Reject return outside a function (language specification).
- Basic scope entry for blocks, functions, and parameters.
- Conservative same-scope redeclaration detection (OQ-01 pending).
"""

from __future__ import annotations

from zen.ast.nodes import (
    AssignExpr,
    BinaryExpr,
    BlockStmt,
    CallExpr,
    Expression,
    ExpressionStmt,
    FunctionDecl,
    GroupingExpr,
    IdentifierExpr,
    IfStmt,
    LiteralExpr,
    Program,
    ReturnStmt,
    Statement,
    UnaryExpr,
    VarDecl,
    WhileStmt,
)

from .diagnostics import SemanticDiagnostic, SemanticError, SemanticSeverity
from .scope import Scope, Symbol, SymbolKind


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.diagnostics: list[SemanticDiagnostic] = []
        self._scope = Scope()

    def analyze(self, program: Program) -> list[SemanticDiagnostic]:
        self.diagnostics.clear()
        self._scope = Scope()
        for stmt in program.statements:
            self._statement(stmt)
        return list(self.diagnostics)

    def analyze_strict(self, program: Program) -> None:
        diags = self.analyze(program)
        for d in diags:
            if d.severity is SemanticSeverity.ERROR:
                raise SemanticError(d.message, d)

    def _statement(self, stmt: Statement) -> None:
        if isinstance(stmt, VarDecl):
            self._var_decl(stmt)
        elif isinstance(stmt, FunctionDecl):
            self._function_decl(stmt)
        elif isinstance(stmt, IfStmt):
            self._if_stmt(stmt)
        elif isinstance(stmt, WhileStmt):
            self._while_stmt(stmt)
        elif isinstance(stmt, ReturnStmt):
            self._return_stmt(stmt)
        elif isinstance(stmt, ExpressionStmt):
            self._expression(stmt.expression)
        elif isinstance(stmt, BlockStmt):
            self._block(stmt)

    def _var_decl(self, node: VarDecl) -> None:
        kind = SymbolKind.CONSTANT if node.is_const else SymbolKind.VARIABLE
        if node.initializer is not None:
            self._expression(node.initializer)
        symbol = Symbol(
            name=node.name,
            kind=kind,
            span=node.span,
            initialized=node.initializer is not None,
        )
        if not self._scope.define(symbol):
            self._error(
                "SEM_REDECL",
                f"Redeclaration of '{node.name}' in the same scope "
                "(OQ-01 policy pending Owner decision)",
                node.span,
            )

    def _function_decl(self, node: FunctionDecl) -> None:
        symbol = Symbol(
            name=node.name,
            kind=SymbolKind.FUNCTION,
            span=node.span,
            arity=len(node.parameters),
        )
        if not self._scope.define(symbol):
            self._error(
                "SEM_REDECL",
                f"Redeclaration of function '{node.name}' in the same scope "
                "(OQ-01 policy pending Owner decision)",
                node.span,
            )
        fn_scope = Scope(parent=self._scope, is_function=True)
        prev = self._scope
        self._scope = fn_scope
        seen: set[str] = set()
        for i, param in enumerate(node.parameters):
            if param in seen:
                span = (
                    node.parameter_spans[i]
                    if i < len(node.parameter_spans)
                    else node.span
                )
                self._error(
                    "SEM_PARAM_DUP",
                    f"Duplicate parameter name '{param}' "
                    "(OQ-08 policy pending Owner decision)",
                    span,
                )
            seen.add(param)
            fn_scope.define(
                Symbol(
                    name=param,
                    kind=SymbolKind.PARAMETER,
                    span=(
                        node.parameter_spans[i]
                        if i < len(node.parameter_spans)
                        else None
                    ),
                    initialized=True,
                )
            )
        self._block(node.body)
        self._scope = prev

    def _if_stmt(self, node: IfStmt) -> None:
        self._expression(node.condition)
        self._block(node.then_branch)
        if node.else_branch is not None:
            if isinstance(node.else_branch, IfStmt):
                self._if_stmt(node.else_branch)
            else:
                self._block(node.else_branch)

    def _while_stmt(self, node: WhileStmt) -> None:
        self._expression(node.condition)
        self._block(node.body)

    def _return_stmt(self, node: ReturnStmt) -> None:
        if not self._scope.in_function():
            self._error(
                "SEM_RETURN_OUTSIDE",
                "'return' is not allowed outside a function",
                node.span,
            )
        if node.value is not None:
            self._expression(node.value)

    def _block(self, node: BlockStmt) -> None:
        block_scope = Scope(parent=self._scope, is_function=False)
        prev = self._scope
        self._scope = block_scope
        for stmt in node.statements:
            self._statement(stmt)
        self._scope = prev

    def _expression(self, expr: Expression) -> None:
        if isinstance(expr, LiteralExpr):
            return
        if isinstance(expr, IdentifierExpr):
            _ = self._scope.resolve(expr.name)
            return
        if isinstance(expr, AssignExpr):
            if isinstance(expr.target, IdentifierExpr):
                sym = self._scope.resolve(expr.target.name)
                if sym is not None and sym.kind is SymbolKind.CONSTANT:
                    self._error(
                        "SEM_CONST_ASSIGN",
                        f"Cannot assign to constant '{expr.target.name}' "
                        "(OQ-03 policy pending Owner decision)",
                        expr.span,
                    )
            self._expression(expr.value)
            return
        if isinstance(expr, BinaryExpr):
            self._expression(expr.left)
            self._expression(expr.right)
            return
        if isinstance(expr, UnaryExpr):
            self._expression(expr.operand)
            return
        if isinstance(expr, CallExpr):
            self._expression(expr.callee)
            for arg in expr.arguments:
                self._expression(arg)
            return
        if isinstance(expr, GroupingExpr):
            self._expression(expr.expression)
            return

    def _error(
        self,
        code: str,
        message: str,
        span: object | None,
    ) -> None:
        from zen.ast.source_span import SourceSpan

        s = span if isinstance(span, SourceSpan) else None
        diag = SemanticDiagnostic(
            code=code,
            message=message,
            severity=SemanticSeverity.ERROR,
            span=s,
        )
        self.diagnostics.append(diag)


def analyze(program: Program) -> list[SemanticDiagnostic]:
    """Convenience entry point: analyze and return diagnostics."""
    return SemanticAnalyzer().analyze(program)
