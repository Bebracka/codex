from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    type: str
    lexeme: str
    literal: object
    line: int
    column: int
