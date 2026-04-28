from __future__ import annotations

from .ast_nodes import (
    AssignmentNode,
    BinaryOpNode,
    CallNode,
    ConditionNode,
    DeclarationNode,
    FunctionDefNode,
    IdentifierNode,
    IfNode,
    NumberNode,
    PrintNode,
    ProgramNode,
    ReturnNode,
    StringNode,
    WhileNode,
)
from .errors import RuntimeError


class FunctionReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class Interpreter:
    def __init__(self):
        self.scopes: list[dict[str, object]] = []
        self.functions: dict[str, FunctionDefNode] = {}
        self.output: list[str] = []

    def execute(self, program: ProgramNode) -> list[str]:
        self.scopes = [{}]
        self.functions = {}
        self.output = []
        for statement in program.statements:
            if isinstance(statement, FunctionDefNode):
                self.functions[statement.name] = statement
        for statement in program.statements:
            if not isinstance(statement, FunctionDefNode):
                self.execute_statement(statement)
        return self.output

    def execute_statement(self, node):
        method = getattr(self, f"execute_{node.__class__.__name__}", None)
        if not method:
            raise ValueError(f"No interpreter handler for {node.__class__.__name__}")
        method(node)

    def execute_FunctionDefNode(self, node: FunctionDefNode):
        return None

    def execute_DeclarationNode(self, node: DeclarationNode):
        if node.value is None:
            self.current_scope()[node.name] = None
            return
        self.current_scope()[node.name] = self.evaluate_expression(node.value)

    def execute_AssignmentNode(self, node: AssignmentNode):
        self.assign_value(node.name, self.evaluate_expression(node.value), node.line, node.column)

    def execute_PrintNode(self, node: PrintNode):
        value = self.evaluate_expression(node.value)
        self.output.append(str(value))

    def execute_ReturnNode(self, node: ReturnNode):
        value = None if node.value is None else self.evaluate_expression(node.value)
        raise FunctionReturnSignal(value)

    def execute_IfNode(self, node: IfNode):
        if self.evaluate_condition(node.condition):
            for statement in node.then_body:
                self.execute_statement(statement)
        else:
            for statement in node.else_body:
                self.execute_statement(statement)

    def execute_WhileNode(self, node: WhileNode):
        while self.evaluate_condition(node.condition):
            for statement in node.body:
                self.execute_statement(statement)

    def evaluate_expression(self, node):
        if isinstance(node, NumberNode):
            return node.value
        if isinstance(node, StringNode):
            return node.value
        if isinstance(node, IdentifierNode):
            return self.resolve_identifier(node.name, node.line, node.column)
        if isinstance(node, CallNode):
            return self.call_function(node)
        if isinstance(node, BinaryOpNode):
            left = self.evaluate_expression(node.left)
            right = self.evaluate_expression(node.right)
            if node.operator == "+":
                if isinstance(left, str) or isinstance(right, str):
                    return f"{left}{right}"
                self.assert_number(left, node.line, node.column)
                self.assert_number(right, node.line, node.column)
                return left + right
            self.assert_number(left, node.line, node.column)
            self.assert_number(right, node.line, node.column)
            if node.operator == "-":
                return left - right
            if node.operator == "*":
                return left * right
            if node.operator == "/":
                if right == 0:
                    raise RuntimeError(
                        "Division by zero during execution.",
                        node.line,
                        node.column,
                        "Ensure the divisor is not zero before dividing.",
                    )
                return left // right
        raise ValueError(f"Unsupported expression node {node.__class__.__name__}")

    def evaluate_condition(self, node: ConditionNode) -> bool:
        left = self.evaluate_expression(node.left)
        right = self.evaluate_expression(node.right)
        if node.operator == "<":
            self.assert_number(left, node.line, node.column)
            self.assert_number(right, node.line, node.column)
            return left < right
        if node.operator == "<=":
            self.assert_number(left, node.line, node.column)
            self.assert_number(right, node.line, node.column)
            return left <= right
        if node.operator == ">":
            self.assert_number(left, node.line, node.column)
            self.assert_number(right, node.line, node.column)
            return left > right
        if node.operator == ">=":
            self.assert_number(left, node.line, node.column)
            self.assert_number(right, node.line, node.column)
            return left >= right
        if node.operator == "==":
            return left == right
        if node.operator == "!=":
            return left != right
        raise ValueError(f"Unsupported condition operator {node.operator}")

    def call_function(self, node: CallNode):
        if node.name not in self.functions:
            raise RuntimeError(
                f"Function '{node.name}' is not available during execution.",
                node.line,
                node.column,
                "Define the function before calling it.",
            )
        function_def = self.functions[node.name]
        if len(node.args) != len(function_def.params):
            raise RuntimeError(
                f"Function '{node.name}' expects {len(function_def.params)} argument(s).",
                node.line,
                node.column,
                "Pass the same number of arguments as parameters.",
            )
        arg_values = [self.evaluate_expression(arg) for arg in node.args]
        self.push_scope()
        for param, value in zip(function_def.params, arg_values):
            self.current_scope()[param] = value
        try:
            for statement in function_def.body:
                self.execute_statement(statement)
        except FunctionReturnSignal as signal:
            return signal.value
        finally:
            self.pop_scope()
        raise RuntimeError(
            f"Function '{node.name}' ended without returning a value.",
            node.line,
            node.column,
            "Add 'return <value>;' to the function body.",
        )

    def resolve_identifier(self, name: str, line: int, column: int):
        for scope in reversed(self.scopes):
            if name in scope:
                value = scope[name]
                if value is None:
                    raise RuntimeError(
                        f"Variable '{name}' is used before initialization.",
                        line,
                        column,
                        "Assign a value before using the variable.",
                    )
                return value
        raise RuntimeError(
            f"Variable '{name}' is not available during execution.",
            line,
            column,
            "Declare the variable before using it.",
        )

    def assign_value(self, name: str, value, line: int, column: int):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return
        raise RuntimeError(
            f"Variable '{name}' is not available during execution.",
            line,
            column,
            "Declare the variable before assigning to it.",
        )

    def assert_number(self, value, line: int, column: int):
        if not isinstance(value, int):
            raise RuntimeError(
                "Runtime expected a numeric value.",
                line,
                column,
                "Use numeric expressions for arithmetic and order comparisons.",
            )

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def current_scope(self) -> dict[str, object]:
        return self.scopes[-1]

    def global_scope(self) -> dict[str, object]:
        return self.scopes[0]
