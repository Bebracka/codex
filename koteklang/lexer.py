from koteklang.errors import LexerError
from koteklang.token import Token


KEYWORDS = {
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "fun": "FUN",
    "return": "RETURN",
    "let": "LET",
    "print": "PRINT",
    "true": "TRUE",
    "false": "FALSE",
    "nil": "NIL",
    "and": "AND",
    "or": "OR",
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_line = 1
        self.start_column = 1

    def tokenize(self) -> list[Token]:
        while not self._is_at_end():
            self.start = self.current
            self.start_line = self.line
            self.start_column = self.column
            self._scan_token()
        self.tokens.append(Token("EOF", "", None, self.line, self.column))
        return self.tokens

    def _scan_token(self) -> None:
        c = self._advance()
        single = {
            "(": "LPAREN",
            ")": "RPAREN",
            "{": "LBRACE",
            "}": "RBRACE",
            "[": "LBRACKET",
            "]": "RBRACKET",
            ",": "COMMA",
            ".": "DOT",
            ";": "SEMICOLON",
            "+": "PLUS",
            "-": "MINUS",
            "*": "STAR",
            "%": "PERCENT",
        }
        if c in single:
            self._add_token(single[c])
            return
        if c == "!":
            self._add_token("BANG_EQUAL" if self._match("=") else "BANG")
        elif c == "=":
            self._add_token("EQUAL_EQUAL" if self._match("=") else "EQUAL")
        elif c == "<":
            self._add_token("LESS_EQUAL" if self._match("=") else "LESS")
        elif c == ">":
            self._add_token("GREATER_EQUAL" if self._match("=") else "GREATER")
        elif c == "/":
            if self._match("/"):
                while self._peek() != "\n" and not self._is_at_end():
                    self._advance()
            else:
                self._add_token("SLASH")
        elif c in {" ", "\r", "\t"}:
            return
        elif c == "\n":
            return
        elif c == '"':
            self._string()
        elif c.isdigit():
            self._number()
        elif c.isalpha() or c == "_":
            self._identifier()
        else:
            raise LexerError(f"Unexpected character '{c}'", self.start_line, self.start_column)

    def _identifier(self) -> None:
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        text = self.source[self.start : self.current]
        token_type = KEYWORDS.get(text, "IDENTIFIER")
        self._add_token(token_type)

    def _number(self) -> None:
        while self._peek().isdigit():
            self._advance()
        if self._peek() == "." and self._peek_next().isdigit():
            self._advance()
            while self._peek().isdigit():
                self._advance()
        text = self.source[self.start : self.current]
        value = float(text) if "." in text else int(text)
        self._add_token("NUMBER", value)

    def _string(self) -> None:
        while self._peek() != '"' and not self._is_at_end():
            self._advance()
        if self._is_at_end():
            raise LexerError("Unterminated string", self.start_line, self.start_column)
        self._advance()
        value = self.source[self.start + 1 : self.current - 1]
        self._add_token("STRING", value)

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        if c == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return c

    def _add_token(self, token_type: str, literal: object = None) -> None:
        text = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, text, literal, self.start_line, self.start_column))
