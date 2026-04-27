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
from .errors import SemanticError


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table: dict[str, dict] = {}

    def analyze(self, program: ProgramNode) -> dict[str, dict]:
        for statement in program.statements:
            self.visit(statement)
        return self.symbol_table

    def visit(self, node):
        method = getattr(self, f"visit_{node.__class__.__name__}", None)
        if not method:
            raise ValueError(f"No semantic visitor for {node.__class__.__name__}")
        return method(node)

    def visit_ProgramNode(self, node: ProgramNode):
        for statement in node.statements:
            self.visit(statement)

    def visit_DeclarationNode(self, node: DeclarationNode):
        if node.name in self.symbol_table:
            raise SemanticError(
                f"Variable '{node.name}' is already declared.",
                node.line,
                node.column,
                "Use a different name or remove the duplicate declaration.",
            )
        entry = {"type": "int", "initialized": False}
        if node.value is not None:
            value_type = self.infer_expression_type(node.value)
            if value_type != "int":
                raise SemanticError(
                    f"Variable '{node.name}' can only be initialized with a numeric expression in version 1.",
                    node.line,
                    node.column,
                    "Use an integer expression for variable values.",
                )
            entry["initialized"] = True
        self.symbol_table[node.name] = entry

    def visit_AssignmentNode(self, node: AssignmentNode):
        symbol = self.require_symbol(node.name, node.line, node.column)
        value_type = self.infer_expression_type(node.value)
        if value_type != "int":
            raise SemanticError(
                f"Variable '{node.name}' can only receive numeric expressions in version 1.",
                node.line,
                node.column,
                "Assign a number or arithmetic expression instead of a string.",
            )
        symbol["initialized"] = True

    def visit_PrintNode(self, node: PrintNode):
        self.infer_expression_type(node.value, allow_string=True)

    def visit_IfNode(self, node: IfNode):
        self.visit_ConditionNode(node.condition)
        for statement in node.then_body:
            self.visit(statement)
        for statement in node.else_body:
            self.visit(statement)

    def visit_WhileNode(self, node: WhileNode):
        self.visit_ConditionNode(node.condition)
        for statement in node.body:
            self.visit(statement)

    def visit_ConditionNode(self, node: ConditionNode):
        left_type = self.infer_expression_type(node.left)
        right_type = self.infer_expression_type(node.right)
        if left_type != "int" or right_type != "int":
            raise SemanticError(
                "Conditions must compare numeric expressions in version 1.",
                node.line,
                node.column,
                "Compare numbers or declared numeric variables only.",
            )

    def infer_expression_type(self, node, allow_string: bool = False) -> str:
        if isinstance(node, NumberNode):
            return "int"
        if isinstance(node, StringNode):
            if allow_string:
                return "string"
            raise SemanticError(
                "String values cannot be used in arithmetic expressions.",
                node.line,
                node.column,
                "Use strings only with print statements in version 1.",
            )
        if isinstance(node, IdentifierNode):
            symbol = self.require_symbol(node.name, node.line, node.column)
            return symbol["type"]
        if isinstance(node, BinaryOpNode):
            left_type = self.infer_expression_type(node.left)
            right_type = self.infer_expression_type(node.right)
            if left_type != "int" or right_type != "int":
                raise SemanticError(
                    "Arithmetic expressions must use numeric values.",
                    node.line,
                    node.column,
                    "Use integers or declared numeric variables here.",
                )
            return "int"
        if isinstance(node, ConditionNode):
            self.visit_ConditionNode(node)
            return "bool"
        raise ValueError(f"Unhandled node type {node.__class__.__name__}")

    def require_symbol(self, name: str, line: int, column: int) -> dict:
        if name not in self.symbol_table:
            raise SemanticError(
                f"Variable '{name}' is used before declaration.",
                line,
                column,
                "Declare the variable first using 'declare variable name;'.",
            )
        return self.symbol_table[name]
