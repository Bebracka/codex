from dataclasses import dataclass

from koteklang import ast
from koteklang.errors import RuntimeError_


class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name: str, value):
        self.values[name] = value

    def get(self, name_token):
        name = name_token.lexeme
        if name in self.values:
            return self.values[name]
        if self.enclosing:
            return self.enclosing.get(name_token)
        raise RuntimeError_(f"Undefined variable '{name}'", name_token.line, name_token.column)

    def assign(self, name_token, value):
        name = name_token.lexeme
        if name in self.values:
            self.values[name] = value
            return
        if self.enclosing:
            self.enclosing.assign(name_token, value)
            return
        raise RuntimeError_(f"Undefined variable '{name}'", name_token.line, name_token.column)


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


@dataclass
class KotekFunction:
    declaration: ast.FunctionStmt
    closure: Environment

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments):
        env = Environment(self.closure)
        for idx, param in enumerate(self.declaration.params):
            env.define(param.lexeme, arguments[idx])
        try:
            interpreter.execute_block(self.declaration.body, env)
        except ReturnSignal as signal:
            return signal.value
        return None

    def __str__(self):
        return f"<fun {self.declaration.name.lexeme}>"


class Interpreter:
    def __init__(self, output=None):
        self.globals = Environment()
        self.environment = self.globals
        self.output = output if output is not None else print

    def interpret(self, statements):
        for stmt in statements:
            self.execute(stmt)

    def execute(self, stmt):
        if isinstance(stmt, ast.ExprStmt):
            self.evaluate(stmt.expression)
        elif isinstance(stmt, ast.PrintStmt):
            value = self.evaluate(stmt.expression)
            self.output(self.stringify(value))
        elif isinstance(stmt, ast.VarStmt):
            value = self.evaluate(stmt.initializer)
            self.environment.define(stmt.name.lexeme, value)
        elif isinstance(stmt, ast.BlockStmt):
            self.execute_block(stmt.statements, Environment(self.environment))
        elif isinstance(stmt, ast.IfStmt):
            if self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.then_branch)
            elif stmt.else_branch is not None:
                self.execute(stmt.else_branch)
        elif isinstance(stmt, ast.WhileStmt):
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.body)
        elif isinstance(stmt, ast.FunctionStmt):
            self.environment.define(stmt.name.lexeme, KotekFunction(stmt, self.environment))
        elif isinstance(stmt, ast.ReturnStmt):
            value = self.evaluate(stmt.value) if stmt.value is not None else None
            raise ReturnSignal(value)

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def evaluate(self, expr):
        if isinstance(expr, ast.Literal):
            return expr.value
        if isinstance(expr, ast.Grouping):
            return self.evaluate(expr.expression)
        if isinstance(expr, ast.Unary):
            right = self.evaluate(expr.right)
            if expr.operator.type == "MINUS":
                self._check_number_operand(expr.operator, right)
                return -right
            if expr.operator.type == "BANG":
                return not self.is_truthy(right)
        if isinstance(expr, ast.Binary):
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)
            t = expr.operator.type
            if t == "PLUS":
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                if isinstance(left, list) and isinstance(right, list):
                    return left + right
                raise RuntimeError_("Operands for '+' must be both numbers, both strings, or both lists", expr.operator.line, expr.operator.column)
            if t == "MINUS":
                self._check_number_operands(expr.operator, left, right)
                return left - right
            if t == "STAR":
                self._check_number_operands(expr.operator, left, right)
                return left * right
            if t == "SLASH":
                self._check_number_operands(expr.operator, left, right)
                return left / right
            if t == "PERCENT":
                self._check_number_operands(expr.operator, left, right)
                return left % right
            if t == "GREATER":
                self._check_number_operands(expr.operator, left, right)
                return left > right
            if t == "GREATER_EQUAL":
                self._check_number_operands(expr.operator, left, right)
                return left >= right
            if t == "LESS":
                self._check_number_operands(expr.operator, left, right)
                return left < right
            if t == "LESS_EQUAL":
                self._check_number_operands(expr.operator, left, right)
                return left <= right
            if t == "EQUAL_EQUAL":
                return left == right
            if t == "BANG_EQUAL":
                return left != right
        if isinstance(expr, ast.Variable):
            return self.environment.get(expr.name)
        if isinstance(expr, ast.Assign):
            value = self.evaluate(expr.value)
            self.environment.assign(expr.name, value)
            return value
        if isinstance(expr, ast.Logical):
            left = self.evaluate(expr.left)
            if expr.operator.type == "OR":
                if self.is_truthy(left):
                    return left
            else:
                if not self.is_truthy(left):
                    return left
            return self.evaluate(expr.right)
        if isinstance(expr, ast.Call):
            callee = self.evaluate(expr.callee)
            arguments = [self.evaluate(argument) for argument in expr.arguments]
            if not hasattr(callee, "call"):
                raise RuntimeError_("Can only call functions", expr.paren.line, expr.paren.column)
            if len(arguments) != callee.arity():
                raise RuntimeError_(
                    f"Expected {callee.arity()} arguments but got {len(arguments)}",
                    expr.paren.line,
                    expr.paren.column,
                )
            return callee.call(self, arguments)
        if isinstance(expr, ast.ListLiteral):
            return [self.evaluate(element) for element in expr.elements]
        if isinstance(expr, ast.Index):
            target = self.evaluate(expr.target)
            index = self.evaluate(expr.index)
            if not isinstance(index, int):
                raise RuntimeError_("List index must be an integer", expr.bracket.line, expr.bracket.column)
            if not isinstance(target, list):
                raise RuntimeError_("Indexing is only supported on lists", expr.bracket.line, expr.bracket.column)
            try:
                return target[index]
            except IndexError as exc:
                raise RuntimeError_("List index out of range", expr.bracket.line, expr.bracket.column) from exc
        raise RuntimeError_("Unknown expression")

    @staticmethod
    def is_truthy(value):
        return not (value is None or value is False)

    @staticmethod
    def stringify(value):
        if value is None:
            return "nil"
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    @staticmethod
    def _check_number_operand(operator, operand):
        if isinstance(operand, (int, float)):
            return
        raise RuntimeError_("Operand must be a number", operator.line, operator.column)

    @staticmethod
    def _check_number_operands(operator, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise RuntimeError_("Operands must be numbers", operator.line, operator.column)
