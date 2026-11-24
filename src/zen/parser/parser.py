"""Zen v0.1 recursive-descent parser.

Implements the official EBNF in docs/03-language-specification.md.
Produces the canonical AST defined in zen.ast.nodes.

This module does not perform semantic analysis.
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
from zen.ast.source_identity import SourceIdentifier
from zen.ast.source_span import SourceSpan
from zen.lexer import Lexer, Token, TokenType
from zen.limits import MAX_PARSER_DEPTH
from zen.parser.context import ParseContext
from zen.parser.diagnostics import ParseError


def parse(
    source: str,
    *,
    source_id: SourceIdentifier | None = None,
) -> Program:
    """Parse Zen source text into a Program AST.

    Raises:
        LexerError: lexical failure.
        ParseError: syntactic failure or parser resource limit.
        TypeError: if source is not a string.
    """
    if not isinstance(source, str):
        raise TypeError("source must be a string")

    if source_id is None:
        source_id = SourceIdentifier.new()

    tokens = Lexer(source).tokenize()
    parser = _Parser(tokens, source_id)
    try:
        return parser.parse_program()
    except RecursionError:
        # Nested expressions can exhaust the Python call stack before
        # MAX_PARSER_DEPTH enters complete (each grouping walks the full
        # expression precedence chain). Surface a controlled ParseError.
        raise ParseError(
            f"Maximum parser nesting depth of {MAX_PARSER_DEPTH} exceeded",
            1,
            1,
            None,
            source_id=source_id,
        ) from None


class _Parser:
    def __init__(
        self,
        tokens: list[Token],
        source_id: SourceIdentifier,
    ) -> None:
        if not tokens:
            raise ValueError("token stream must not be empty")
        if tokens[-1].type is not TokenType.EOF:
            raise ValueError("token stream must end with EOF")

        self.tokens = tokens
        self.source_id = source_id
        self.current = 0
        self.ctx = ParseContext.initial(source_id=source_id)

    def parse_program(self) -> Program:
        statements: list[Statement] = []
        self._skip_separators()

        while not self._is_at_end():
            statements.append(self._statement())
            if self._is_at_end():
                break
            if not self._match(TokenType.NEWLINE, TokenType.SEMICOLON):
                self._error_at_current(
                    "Expected newline or semicolon between statements"
                )
            self._skip_separators()

        start = self.tokens[0]
        end = self._previous() if self.current > 0 else start
        span = self._span_from_tokens(start, end)
        self.ctx = self.ctx.track_node(span)
        return Program(
            span=span,
            statements=tuple(statements),
            source_id=self.source_id,
        )

    def _statement(self) -> Statement:
        if self._check(TokenType.LET) or self._check(TokenType.CONST):
            return self._var_declaration()
        if self._check(TokenType.FN):
            return self._function_declaration()
        if self._check(TokenType.IF):
            return self._if_statement()
        if self._check(TokenType.WHILE):
            return self._while_statement()
        if self._check(TokenType.RETURN):
            return self._return_statement()
        return self._expression_statement()

    def _var_declaration(self) -> VarDecl:
        start = self._peek()
        is_const = self._match(TokenType.CONST)
        if not is_const:
            self._consume(TokenType.LET, "Expected 'let' or 'const'")

        name_tok = self._consume(
            TokenType.IDENTIFIER,
            "Expected variable name",
        )
        initializer: Expression | None = None

        if is_const:
            self._consume(
                TokenType.ASSIGN,
                "const declaration requires an initializer",
            )
            initializer = self._expression()
        elif self._match(TokenType.ASSIGN):
            initializer = self._expression()

        end = self._previous()
        span = self._span_from_tokens(start, end)
        self.ctx = self.ctx.track_node(span)
        return VarDecl(
            span=span,
            name=name_tok.lexeme,
            initializer=initializer,
            is_const=is_const,
            source_id=self.source_id,
        )

    def _function_declaration(self) -> FunctionDecl:
        start = self._consume(TokenType.FN, "Expected 'fn'")
        name_tok = self._consume(
            TokenType.IDENTIFIER,
            "Expected function name",
        )
        name_span = self._token_span(name_tok)

        self._consume(TokenType.LEFT_PAREN, "Expected '(' after function name")
        parameters: list[str] = []
        parameter_spans: list[SourceSpan] = []

        self._skip_newlines_only()
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                self._skip_newlines_only()
                param = self._consume(
                    TokenType.IDENTIFIER,
                    "Expected parameter name",
                )
                parameters.append(param.lexeme)
                parameter_spans.append(self._token_span(param))
                self._skip_newlines_only()
                if not self._match(TokenType.COMMA):
                    break
                self._skip_newlines_only()
                if self._check(TokenType.RIGHT_PAREN):
                    self._error_at_current(
                        "Trailing comma in parameter list is not allowed"
                    )

        self._skip_newlines_only()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        body = self._block()
        span = self._span_from_tokens(start, self._previous())
        self.ctx = self.ctx.track_node(span)
        return FunctionDecl(
            span=span,
            name=name_tok.lexeme,
            parameters=tuple(parameters),
            body=body,
            name_span=name_span,
            parameter_spans=tuple(parameter_spans),
            source_id=self.source_id,
        )

    def _if_statement(self) -> IfStmt:
        start = self._consume(TokenType.IF, "Expected 'if'")
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'")
        self._skip_newlines_only()
        condition = self._expression()
        self._skip_newlines_only()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after condition")
        then_branch = self._block()

        else_branch: BlockStmt | IfStmt | None = None
        saved = self.current
        while self._check(TokenType.NEWLINE):
            self._advance()
        if self._match(TokenType.ELSE):
            if self._check(TokenType.IF):
                else_branch = self._if_statement()
            else:
                else_branch = self._block()
        else:
            self.current = saved

        span = self._span_from_tokens(start, self._previous())
        self.ctx = self.ctx.track_node(span)
        return IfStmt(
            span=span,
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
            source_id=self.source_id,
        )

    def _while_statement(self) -> WhileStmt:
        start = self._consume(TokenType.WHILE, "Expected 'while'")
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'")
        self._skip_newlines_only()
        condition = self._expression()
        self._skip_newlines_only()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after condition")
        body = self._block()
        span = self._span_from_tokens(start, self._previous())
        self.ctx = self.ctx.track_node(span)
        return WhileStmt(
            span=span,
            condition=condition,
            body=body,
            source_id=self.source_id,
        )

    def _return_statement(self) -> ReturnStmt:
        start = self._consume(TokenType.RETURN, "Expected 'return'")
        value: Expression | None = None

        if not self._check_any(
            TokenType.NEWLINE,
            TokenType.SEMICOLON,
            TokenType.RIGHT_BRACE,
            TokenType.EOF,
        ):
            value = self._expression()

        end = self._previous()
        span = self._span_from_tokens(start, end)
        self.ctx = self.ctx.track_node(span)
        return ReturnStmt(
            span=span,
            value=value,
            source_id=self.source_id,
        )

    def _expression_statement(self) -> ExpressionStmt:
        expr = self._expression()
        span = expr.span
        self.ctx = self.ctx.track_node(span)
        return ExpressionStmt(
            span=span,
            expression=expr,
            source_id=self.source_id,
        )

    def _push_depth(self, span: SourceSpan) -> ParseContext:
        """Enter nested depth; return previous context for restore."""
        previous = self.ctx
        self.ctx = self.ctx.enter(span)
        return previous

    def _pop_depth(self, previous: ParseContext) -> None:
        """Restore outer depth; keep cumulative node_count."""
        self.ctx = ParseContext(
            depth=previous.depth,
            node_count=self.ctx.node_count,
            source_id=self.source_id,
        )

    def _block(self) -> BlockStmt:
        start = self._consume(TokenType.LEFT_BRACE, "Expected '{'")
        previous_ctx = self.ctx
        self.ctx = self.ctx.enter(self._token_span(start))

        statements: list[Statement] = []
        self._skip_separators()
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self._statement())
            if self._check(TokenType.RIGHT_BRACE) or self._is_at_end():
                break
            if not self._match(TokenType.NEWLINE, TokenType.SEMICOLON):
                self._error_at_current(
                    "Expected newline or semicolon between statements"
                )
            self._skip_separators()

        end = self._consume(TokenType.RIGHT_BRACE, "Expected '}' after block")

        span = self._span_from_tokens(start, end)
        self.ctx = ParseContext(
            depth=previous_ctx.depth,
            node_count=self.ctx.node_count,
            source_id=self.source_id,
        ).track_node(span)
        return BlockStmt(
            span=span,
            statements=tuple(statements),
            source_id=self.source_id,
        )

    def _expression(self) -> Expression:
        return self._assignment()

    def _assignment(self) -> Expression:
        if self._check(TokenType.IDENTIFIER) and self._check_next(
            TokenType.ASSIGN
        ):
            name_tok = self._advance()
            self._advance()
            target_span = self._token_span(name_tok)
            previous = self._push_depth(target_span)
            try:
                value = self._assignment()
            finally:
                self._pop_depth(previous)
            self.ctx = self.ctx.track_node(target_span)
            target = IdentifierExpr(
                span=target_span,
                name=name_tok.lexeme,
                source_id=self.source_id,
            )
            span = self._span_merge(target.span, value.span)
            self.ctx = self.ctx.track_node(span)
            return AssignExpr(
                span=span,
                target=target,
                value=value,
                source_id=self.source_id,
            )
        return self._logical_or()

    def _logical_or(self) -> Expression:
        expr = self._logical_and()
        while self._match(TokenType.OR):
            op = self._previous()
            right = self._logical_and()
            expr = self._binary(expr, op.lexeme, right)
        return expr

    def _logical_and(self) -> Expression:
        expr = self._equality()
        while self._match(TokenType.AND):
            op = self._previous()
            right = self._equality()
            expr = self._binary(expr, op.lexeme, right)
        return expr

    def _equality(self) -> Expression:
        expr = self._comparison()
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            op = self._previous()
            right = self._comparison()
            expr = self._binary(expr, op.lexeme, right)
        return expr

    def _comparison(self) -> Expression:
        expr = self._term()
        while self._match(
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ):
            op = self._previous()
            right = self._term()
            expr = self._binary(expr, op.lexeme, right)
        return expr

    def _term(self) -> Expression:
        expr = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous()
            right = self._factor()
            expr = self._binary(expr, op.lexeme, right)
        return expr

    def _factor(self) -> Expression:
        expr = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._previous()
            right = self._unary()
            expr = self._binary(expr, op.lexeme, right)
        return expr

    def _unary(self) -> Expression:
        if self._match(TokenType.BANG, TokenType.MINUS):
            op = self._previous()
            op_span = self._token_span(op)
            previous = self._push_depth(op_span)
            try:
                operand = self._unary()
            finally:
                self._pop_depth(previous)
            span = self._span_merge(op_span, operand.span)
            self.ctx = self.ctx.track_node(span)
            return UnaryExpr(
                span=span,
                operator=op.lexeme,
                operand=operand,
                source_id=self.source_id,
            )
        return self._call()

    def _call(self) -> Expression:
        expr = self._primary()
        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            else:
                break
        return expr

    def _finish_call(self, callee: Expression) -> CallExpr:
        args: list[Expression] = []
        self._skip_newlines_only()
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                self._skip_newlines_only()
                args.append(self._expression())
                self._skip_newlines_only()
                if not self._match(TokenType.COMMA):
                    break
                self._skip_newlines_only()
                if self._check(TokenType.RIGHT_PAREN):
                    self._error_at_current(
                        "Trailing comma in argument list is not allowed"
                    )
        self._skip_newlines_only()
        end = self._consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
        span = self._span_merge(callee.span, self._token_span(end))
        self.ctx = self.ctx.track_node(span)
        return CallExpr(
            span=span,
            callee=callee,
            arguments=tuple(args),
            source_id=self.source_id,
        )

    def _primary(self) -> Expression:
        if self._match(TokenType.TRUE):
            tok = self._previous()
            span = self._token_span(tok)
            self.ctx = self.ctx.track_node(span)
            return LiteralExpr(span=span, value=True, source_id=self.source_id)

        if self._match(TokenType.FALSE):
            tok = self._previous()
            span = self._token_span(tok)
            self.ctx = self.ctx.track_node(span)
            return LiteralExpr(span=span, value=False, source_id=self.source_id)

        if self._match(TokenType.NULL):
            tok = self._previous()
            span = self._token_span(tok)
            self.ctx = self.ctx.track_node(span)
            return LiteralExpr(span=span, value=None, source_id=self.source_id)

        if self._match(TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING):
            tok = self._previous()
            span = self._token_span(tok)
            self.ctx = self.ctx.track_node(span)
            return LiteralExpr(
                span=span,
                value=tok.literal,
                source_id=self.source_id,
            )

        if self._match(TokenType.IDENTIFIER):
            tok = self._previous()
            span = self._token_span(tok)
            self.ctx = self.ctx.track_node(span)
            return IdentifierExpr(
                span=span,
                name=tok.lexeme,
                source_id=self.source_id,
            )

        if self._match(TokenType.LEFT_PAREN):
            open_tok = self._previous()
            open_span = self._token_span(open_tok)
            previous = self._push_depth(open_span)
            try:
                self._skip_newlines_only()
                expr = self._expression()
                self._skip_newlines_only()
                close_tok = self._consume(
                    TokenType.RIGHT_PAREN,
                    "Expected ')' after expression",
                )
            finally:
                self._pop_depth(previous)
            span = self._span_from_tokens(open_tok, close_tok)
            self.ctx = self.ctx.track_node(span)
            return GroupingExpr(
                span=span,
                expression=expr,
                source_id=self.source_id,
            )

        self._error_at_current("Expected expression")

    def _binary(
        self,
        left: Expression,
        operator: str,
        right: Expression,
    ) -> BinaryExpr:
        span = self._span_merge(left.span, right.span)
        self.ctx = self.ctx.track_node(span)
        return BinaryExpr(
            span=span,
            left=left,
            operator=operator,
            right=right,
            source_id=self.source_id,
        )

    def _skip_separators(self) -> None:
        while self._match(TokenType.NEWLINE, TokenType.SEMICOLON):
            pass

    def _skip_newlines_only(self) -> None:
        while self._match(TokenType.NEWLINE):
            pass

    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return token_type is TokenType.EOF
        return self._peek().type is token_type

    def _check_any(self, *types: TokenType) -> bool:
        return any(self._check(t) for t in types)

    def _check_next(self, token_type: TokenType) -> bool:
        if self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].type is token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type is TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        self._error_at_current(message)

    def _error_at_current(self, message: str) -> None:
        tok = self._peek()
        span = self._token_span(tok)
        raise ParseError(
            message,
            tok.line,
            tok.column,
            span,
            source_id=self.source_id,
        )

    def _token_span(self, token: Token) -> SourceSpan:
        if token.type is TokenType.EOF:
            return SourceSpan(
                token.line,
                token.column,
                token.line,
                token.column,
            )
        if token.type is TokenType.NEWLINE:
            return SourceSpan(
                token.line,
                token.column,
                token.line + 1,
                1,
            )
        length = max(1, len(token.lexeme))
        return SourceSpan(
            token.line,
            token.column,
            token.line,
            token.column + length,
        )

    def _span_from_tokens(self, start: Token, end: Token) -> SourceSpan:
        s = self._token_span(start)
        e = self._token_span(end)
        return SourceSpan(
            s.start_line,
            s.start_column,
            e.end_line,
            e.end_column,
        )

    def _span_merge(self, a: SourceSpan, b: SourceSpan) -> SourceSpan:
        start_line, start_col = a.start_line, a.start_column
        end_line, end_col = b.end_line, b.end_column
        if (b.start_line, b.start_column) < (start_line, start_col):
            start_line, start_col = b.start_line, b.start_column
        if (a.end_line, a.end_column) > (end_line, end_col):
            end_line, end_col = a.end_line, a.end_column
        return SourceSpan(start_line, start_col, end_line, end_col)
