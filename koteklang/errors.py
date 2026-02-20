class KotekLangError(Exception):
    """Base language error with optional source location."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.__str__())

    def __str__(self) -> str:
        if self.line is not None and self.column is not None:
            return f"{self.message} (line {self.line}, col {self.column})"
        return self.message


class LexerError(KotekLangError):
    pass


class ParserError(KotekLangError):
    pass


class RuntimeError_(KotekLangError):
    pass
