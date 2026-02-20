from dataclasses import dataclass


class Expr:
    pass


@dataclass
class Literal(Expr):
    value: object


@dataclass
class Variable(Expr):
    name: object


@dataclass
class Assign(Expr):
    name: object
    value: Expr


@dataclass
class Grouping(Expr):
    expression: Expr


@dataclass
class Unary(Expr):
    operator: object
    right: Expr


@dataclass
class Binary(Expr):
    left: Expr
    operator: object
    right: Expr


@dataclass
class Logical(Expr):
    left: Expr
    operator: object
    right: Expr


@dataclass
class Call(Expr):
    callee: Expr
    paren: object
    arguments: list[Expr]


@dataclass
class ListLiteral(Expr):
    elements: list[Expr]


@dataclass
class Index(Expr):
    target: Expr
    index: Expr
    bracket: object


class Stmt:
    pass


@dataclass
class ExprStmt(Stmt):
    expression: Expr


@dataclass
class PrintStmt(Stmt):
    expression: Expr


@dataclass
class VarStmt(Stmt):
    name: object
    initializer: Expr


@dataclass
class BlockStmt(Stmt):
    statements: list[Stmt]


@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: Stmt


@dataclass
class FunctionStmt(Stmt):
    name: object
    params: list[object]
    body: list[Stmt]


@dataclass
class ReturnStmt(Stmt):
    keyword: object
    value: Expr | None
