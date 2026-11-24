"""Semantic analyzer — OQ-01..OQ-09 with symbol-identity definite assignment."""
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
from zen.ast.source_span import SourceSpan

from .diagnostics import (
    ZSS_S001_UNDEFINED,
    ZSS_S002_DUPLICATE,
    ZSS_S003_UNINITIALIZED,
    ZSS_S004_CONST_ASSIGN,
    ZSS_S005_NOT_CALLABLE,
    ZSS_S006_ARITY,
    ZSS_S007_DUP_PARAM,
    ZSS_S008_RETURN_OUTSIDE,
    SemanticDiagnostic,
    SemanticError,
    SemanticSeverity,
)
from .scope import Scope, Symbol, SymbolKind


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.diagnostics: list[SemanticDiagnostic] = []
        self._scope = Scope()
        # Definite assignment tracks Symbol object identity, not bare names.
        self._initialized: set[int] = set()

    def analyze(self, program: Program) -> list[SemanticDiagnostic]:
        self.diagnostics.clear()
        self._scope = Scope()
        self._initialized = set()
        for stmt in program.statements:
            self._statement(stmt)
        self.diagnostics.sort(
            key=lambda d: (
                d.span.start_line if d.span else 0,
                d.span.start_column if d.span else 0,
                d.code,
            )
        )
        return list(self.diagnostics)

    def analyze_strict(self, program: Program) -> None:
        for d in self.analyze(program):
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
        existing = self._scope.resolve_local(node.name)
        if existing is not None:
            related = existing.span if isinstance(existing.span, SourceSpan) else None
            self._error(
                ZSS_S002_DUPLICATE,
                f"Duplicate declaration of '{node.name}' in the same scope",
                node.span,
                symbol=node.name,
                related=related,
            )
            return
        self._scope.define(symbol)
        if node.initializer is not None:
            self._initialized.add(id(symbol))

    def _function_decl(self, node: FunctionDecl) -> None:
        symbol = Symbol(
            name=node.name,
            kind=SymbolKind.FUNCTION,
            span=node.span,
            arity=len(node.parameters),
            initialized=True,
        )
        existing = self._scope.resolve_local(node.name)
        if existing is not None:
            related = existing.span if isinstance(existing.span, SourceSpan) else None
            self._error(
                ZSS_S002_DUPLICATE,
                f"Duplicate declaration of '{node.name}' in the same scope",
                node.span,
                symbol=node.name,
                related=related,
            )
        else:
            self._scope.define(symbol)
            self._initialized.add(id(symbol))

        fn_scope = Scope(parent=self._scope, is_function=True)
        prev_scope = self._scope
        prev_init = set(self._initialized)
        self._scope = fn_scope
        self._initialized = set(prev_init)
        if existing is None:
            self._initialized.add(id(symbol))

        seen: set[str] = set()
        for i, param in enumerate(node.parameters):
            pspan = (
                node.parameter_spans[i]
                if i < len(node.parameter_spans)
                else node.span
            )
            if param in seen:
                self._error(
                    ZSS_S007_DUP_PARAM,
                    f"Duplicate parameter name '{param}'",
                    pspan,
                    symbol=param,
                )
            seen.add(param)
            psym = Symbol(
                name=param,
                kind=SymbolKind.PARAMETER,
                span=pspan,
                initialized=True,
            )
            fn_scope.define(psym)
            self._initialized.add(id(psym))

        self._block(node.body)
        self._scope = prev_scope
        self._initialized = prev_init

    def _if_stmt(self, node: IfStmt) -> None:
        self._expression(node.condition)
        saved = set(self._initialized)
        self._block(node.then_branch)
        then_init = set(self._initialized)
        if node.else_branch is not None:
            self._initialized = set(saved)
            if isinstance(node.else_branch, IfStmt):
                self._if_stmt(node.else_branch)
            else:
                self._block(node.else_branch)
            self._initialized = then_init & set(self._initialized)
        else:
            self._initialized = saved

    def _while_stmt(self, node: WhileStmt) -> None:
        self._expression(node.condition)
        saved = set(self._initialized)
        self._block(node.body)
        self._initialized = saved

    def _return_stmt(self, node: ReturnStmt) -> None:
        if not self._scope.in_function():
            self._error(
                ZSS_S008_RETURN_OUTSIDE,
                "'return' is not allowed outside a function",
                node.span,
            )
        if node.value is not None:
            self._expression(node.value)

    def _block(self, node: BlockStmt) -> None:
        prev = self._scope
        self._scope = Scope(parent=self._scope, is_function=False)
        for stmt in node.statements:
            self._statement(stmt)
        self._scope = prev

    def _expression(self, expr: Expression) -> None:
        if isinstance(expr, LiteralExpr):
            return
        if isinstance(expr, IdentifierExpr):
            sym = self._scope.resolve(expr.name)
            if sym is None:
                self._error(
                    ZSS_S001_UNDEFINED,
                    f"Undefined identifier '{expr.name}'",
                    expr.span,
                    symbol=expr.name,
                )
            elif sym.kind is SymbolKind.VARIABLE and id(sym) not in self._initialized:
                self._error(
                    ZSS_S003_UNINITIALIZED,
                    f"Variable '{expr.name}' may be read before initialization",
                    expr.span,
                    symbol=expr.name,
                )
            return
        if isinstance(expr, AssignExpr):
            if isinstance(expr.target, IdentifierExpr):
                name = expr.target.name
                sym = self._scope.resolve(name)
                if sym is None:
                    self._error(
                        ZSS_S001_UNDEFINED,
                        f"Undefined identifier '{name}'",
                        expr.target.span,
                        symbol=name,
                    )
                elif sym.kind is SymbolKind.CONSTANT:
                    related = (
                        sym.span if isinstance(sym.span, SourceSpan) else None
                    )
                    self._error(
                        ZSS_S004_CONST_ASSIGN,
                        f"Cannot assign to constant '{name}'",
                        expr.span,
                        symbol=name,
                        related=related,
                    )
                elif sym.kind is SymbolKind.FUNCTION:
                    self._error(
                        ZSS_S004_CONST_ASSIGN,
                        f"Cannot assign to function '{name}'",
                        expr.span,
                        symbol=name,
                    )
                self._expression(expr.value)
                if sym is not None and sym.kind is SymbolKind.VARIABLE:
                    self._initialized.add(id(sym))
            else:
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
            callee = expr.callee
            if isinstance(callee, IdentifierExpr):
                sym = self._scope.resolve(callee.name)
                if sym is None:
                    self._error(
                        ZSS_S001_UNDEFINED,
                        f"Undefined identifier '{callee.name}'",
                        callee.span,
                        symbol=callee.name,
                    )
                elif sym.kind is not SymbolKind.FUNCTION:
                    self._error(
                        ZSS_S005_NOT_CALLABLE,
                        f"'{callee.name}' is not a function",
                        expr.span,
                        symbol=callee.name,
                    )
                elif sym.arity is not None and len(expr.arguments) != sym.arity:
                    self._error(
                        ZSS_S006_ARITY,
                        f"Function '{callee.name}' expects {sym.arity} "
                        f"argument(s) but got {len(expr.arguments)}",
                        expr.span,
                        symbol=callee.name,
                    )
            else:
                self._expression(callee)
                self._error(
                    ZSS_S005_NOT_CALLABLE,
                    "Only declared functions are callable",
                    expr.span,
                )
            for arg in expr.arguments:
                self._expression(arg)
            return
        if isinstance(expr, GroupingExpr):
            self._expression(expr.expression)

    def _error(
        self,
        code: str,
        message: str,
        span: object | None,
        *,
        symbol: str | None = None,
        related: SourceSpan | None = None,
    ) -> None:
        s = span if isinstance(span, SourceSpan) else None
        self.diagnostics.append(
            SemanticDiagnostic(
                code=code,
                message=message,
                severity=SemanticSeverity.ERROR,
                span=s,
                symbol=symbol,
                related_span=related,
            )
        )


def analyze(program: Program) -> list[SemanticDiagnostic]:
    return SemanticAnalyzer().analyze(program)
