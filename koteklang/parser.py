from koteklang import ast
from koteklang.errors import ParserError


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements = []
        while not self._is_at_end():
            statements.append(self._declaration())
        return statements

    def _declaration(self):
        if self._match("FUN"):
            return self._function_declaration()
        if self._match("LET"):
            return self._var_declaration()
        return self._statement()

    def _function_declaration(self):
        name = self._consume("IDENTIFIER", "Expected function name")
        self._consume("LPAREN", "Expected '(' after function name")
        params = []
        if not self._check("RPAREN"):
            while True:
                params.append(self._consume("IDENTIFIER", "Expected parameter name"))
                if not self._match("COMMA"):
                    break
        self._consume("RPAREN", "Expected ')' after parameters")
        self._consume("LBRACE", "Expected '{' before function body")
        body = self._block()
        return ast.FunctionStmt(name, params, body)

    def _var_declaration(self):
        name = self._consume("IDENTIFIER", "Expected variable name")
        self._consume("EQUAL", "Expected '=' after variable name")
        initializer = self._expression()
        self._consume("SEMICOLON", "Expected ';' after variable declaration")
        return ast.VarStmt(name, initializer)

    def _statement(self):
        if self._match("PRINT"):
            value = self._expression()
            self._consume("SEMICOLON", "Expected ';' after value")
            return ast.PrintStmt(value)
        if self._match("IF"):
            return self._if_statement()
        if self._match("WHILE"):
            return self._while_statement()
        if self._match("RETURN"):
            return self._return_statement()
        if self._match("LBRACE"):
            return ast.BlockStmt(self._block())
        return self._expression_statement()

    def _if_statement(self):
        self._consume("LPAREN", "Expected '(' after if")
        condition = self._expression()
        self._consume("RPAREN", "Expected ')' after if condition")
        then_branch = self._statement()
        else_branch = self._statement() if self._match("ELSE") else None
        return ast.IfStmt(condition, then_branch, else_branch)

    def _while_statement(self):
        self._consume("LPAREN", "Expected '(' after while")
        condition = self._expression()
        self._consume("RPAREN", "Expected ')' after condition")
        body = self._statement()
        return ast.WhileStmt(condition, body)

    def _return_statement(self):
        keyword = self._previous()
        value = None
        if not self._check("SEMICOLON"):
            value = self._expression()
        self._consume("SEMICOLON", "Expected ';' after return value")
        return ast.ReturnStmt(keyword, value)

    def _block(self):
        statements = []
        while not self._check("RBRACE") and not self._is_at_end():
            statements.append(self._declaration())
        self._consume("RBRACE", "Expected '}' after block")
        return statements

    def _expression_statement(self):
        expr = self._expression()
        self._consume("SEMICOLON", "Expected ';' after expression")
        return ast.ExprStmt(expr)

    def _expression(self):
        return self._assignment()

    def _assignment(self):
        expr = self._or()
        if self._match("EQUAL"):
            equals = self._previous()
            value = self._assignment()
            if isinstance(expr, ast.Variable):
                return ast.Assign(expr.name, value)
            raise ParserError("Invalid assignment target", equals.line, equals.column)
        return expr

    def _or(self):
        expr = self._and()
        while self._match("OR"):
            operator = self._previous()
            right = self._and()
            expr = ast.Logical(expr, operator, right)
        return expr

    def _and(self):
        expr = self._equality()
        while self._match("AND"):
            operator = self._previous()
            right = self._equality()
            expr = ast.Logical(expr, operator, right)
        return expr

    def _equality(self):
        expr = self._comparison()
        while self._match("BANG_EQUAL", "EQUAL_EQUAL"):
            operator = self._previous()
            right = self._comparison()
            expr = ast.Binary(expr, operator, right)
        return expr

    def _comparison(self):
        expr = self._term()
        while self._match("GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"):
            operator = self._previous()
            right = self._term()
            expr = ast.Binary(expr, operator, right)
        return expr

    def _term(self):
        expr = self._factor()
        while self._match("PLUS", "MINUS"):
            operator = self._previous()
            right = self._factor()
            expr = ast.Binary(expr, operator, right)
        return expr

    def _factor(self):
        expr = self._unary()
        while self._match("STAR", "SLASH", "PERCENT"):
            operator = self._previous()
            right = self._unary()
            expr = ast.Binary(expr, operator, right)
        return expr

    def _unary(self):
        if self._match("BANG", "MINUS"):
            operator = self._previous()
            right = self._unary()
            return ast.Unary(operator, right)
        return self._call()

    def _call(self):
        expr = self._primary()
        while True:
            if self._match("LPAREN"):
                expr = self._finish_call(expr)
            elif self._match("LBRACKET"):
                index = self._expression()
                bracket = self._consume("RBRACKET", "Expected ']' after index")
                expr = ast.Index(expr, index, bracket)
            else:
                break
        return expr

    def _finish_call(self, callee):
        arguments = []
        if not self._check("RPAREN"):
            while True:
                arguments.append(self._expression())
                if not self._match("COMMA"):
                    break
        paren = self._consume("RPAREN", "Expected ')' after arguments")
        return ast.Call(callee, paren, arguments)

    def _primary(self):
        if self._match("FALSE"):
            return ast.Literal(False)
        if self._match("TRUE"):
            return ast.Literal(True)
        if self._match("NIL"):
            return ast.Literal(None)
        if self._match("NUMBER", "STRING"):
            return ast.Literal(self._previous().literal)
        if self._match("IDENTIFIER"):
            return ast.Variable(self._previous())
        if self._match("LPAREN"):
            expr = self._expression()
            self._consume("RPAREN", "Expected ')' after expression")
            return ast.Grouping(expr)
        if self._match("LBRACKET"):
            elements = []
            if not self._check("RBRACKET"):
                while True:
                    elements.append(self._expression())
                    if not self._match("COMMA"):
                        break
            self._consume("RBRACKET", "Expected ']' after list")
            return ast.ListLiteral(elements)
        token = self._peek()
        raise ParserError("Expected expression", token.line, token.column)

    def _match(self, *types):
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _consume(self, token_type, message):
        if self._check(token_type):
            return self._advance()
        token = self._peek()
        raise ParserError(message, token.line, token.column)

    def _check(self, token_type):
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _advance(self):
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self):
        return self._peek().type == "EOF"

    def _peek(self):
        return self.tokens[self.current]

    def _previous(self):
        return self.tokens[self.current - 1]
