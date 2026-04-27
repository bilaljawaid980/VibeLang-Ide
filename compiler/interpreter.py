from __future__ import annotations

from .ast_nodes import (
    AssignmentNode,
    BinaryOpNode,
    ConditionNode,
    DeclarationNode,
    IdentifierNode,
    IfNode,
    NumberNode,
    PrintNode,
    ProgramNode,
    StringNode,
    WhileNode,
)
from .errors import RuntimeError


class Interpreter:
    def __init__(self):
        self.env: dict[str, int] = {}
        self.output: list[str] = []

    def execute(self, program: ProgramNode) -> list[str]:
        self.env = {}
        self.output = []
        for statement in program.statements:
            self.execute_statement(statement)
        return self.output

    def execute_statement(self, node):
        method = getattr(self, f"execute_{node.__class__.__name__}", None)
        if not method:
            raise ValueError(f"No interpreter handler for {node.__class__.__name__}")
        method(node)

    def execute_DeclarationNode(self, node: DeclarationNode):
        if node.value is None:
            self.env[node.name] = 0
            return
        value = self.evaluate_expression(node.value)
        self.assert_number(value, node.line, node.column)
        self.env[node.name] = value

    def execute_AssignmentNode(self, node: AssignmentNode):
        self.require_declared(node.name, node.line, node.column)
        value = self.evaluate_expression(node.value)
        self.assert_number(value, node.line, node.column)
        self.env[node.name] = value

    def execute_PrintNode(self, node: PrintNode):
        value = self.evaluate_expression(node.value)
        self.output.append(str(value))

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
            self.require_declared(node.name, node.line, node.column)
            return self.env[node.name]
        if isinstance(node, BinaryOpNode):
            left = self.evaluate_expression(node.left)
            right = self.evaluate_expression(node.right)
            self.assert_number(left, node.line, node.column)
            self.assert_number(right, node.line, node.column)
            if node.operator == "+":
                return left + right
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
        self.assert_number(left, node.line, node.column)
        self.assert_number(right, node.line, node.column)
        if node.operator == "<":
            return left < right
        if node.operator == "<=":
            return left <= right
        if node.operator == ">":
            return left > right
        if node.operator == ">=":
            return left >= right
        if node.operator == "==":
            return left == right
        if node.operator == "!=":
            return left != right
        raise ValueError(f"Unsupported condition operator {node.operator}")

    def require_declared(self, name: str, line: int, column: int):
        if name not in self.env:
            raise RuntimeError(
                f"Variable '{name}' is not available during execution.",
                line,
                column,
                "Declare the variable before using it.",
            )

    def assert_number(self, value, line: int, column: int):
        if not isinstance(value, int):
            raise RuntimeError(
                "Runtime expected a numeric value.",
                line,
                column,
                "Use numeric expressions for arithmetic and conditions.",
            )
