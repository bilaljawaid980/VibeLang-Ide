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
from .errors import SemanticError


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table: dict[str, dict] = {}
        self.function_table: dict[str, dict] = {}
        self.scopes: list[dict[str, dict]] = []
        self.current_function: str | None = None

    def analyze(self, program: ProgramNode) -> dict[str, dict]:
        self.symbol_table = {}
        self.function_table = {}
        self.scopes = [self.symbol_table]
        self.current_function = None

        for statement in program.statements:
            if isinstance(statement, FunctionDefNode):
                self.collect_function(statement)

        for statement in program.statements:
            self.visit(statement)

        return {"variables": self.symbol_table, "functions": self.function_table}

    def collect_function(self, node: FunctionDefNode):
        if node.name in self.function_table:
            raise SemanticError(
                f"Function '{node.name}' is already declared.",
                node.line,
                node.column,
                "Rename or remove the duplicate function definition.",
            )
        self.function_table[node.name] = {"params": node.params, "return_type": None}

    def visit(self, node):
        method = getattr(self, f"visit_{node.__class__.__name__}", None)
        if not method:
            raise ValueError(f"No semantic visitor for {node.__class__.__name__}")
        return method(node)

    def visit_ProgramNode(self, node: ProgramNode):
        for statement in node.statements:
            self.visit(statement)

    def visit_FunctionDefNode(self, node: FunctionDefNode):
        signature = self.function_table[node.name]
        self.current_function = node.name
        self.push_scope()
        for param in node.params:
            self.current_scope()[param] = {"type": "any", "initialized": True}
        for statement in node.body:
            self.visit(statement)
        has_return = self.body_contains_return(node.body)
        self.pop_scope()
        self.current_function = None
        if not has_return and signature["return_type"] is None:
            raise SemanticError(
                f"Function '{node.name}' must include at least one return statement.",
                node.line,
                node.column,
                "Add 'return <value>;' before 'end function;'.",
            )

    def visit_DeclarationNode(self, node: DeclarationNode):
        scope = self.current_scope()
        if node.name in scope:
            raise SemanticError(
                f"Variable '{node.name}' is already declared.",
                node.line,
                node.column,
                "Use a different name or remove the duplicate declaration.",
            )
        entry = {"type": "any", "initialized": False}
        if node.value is not None:
            value_type = self.infer_expression_type(node.value)
            entry["type"] = value_type
            entry["initialized"] = True
        scope[node.name] = entry

    def visit_AssignmentNode(self, node: AssignmentNode):
        symbol = self.lookup_symbol(node.name, node.line, node.column)
        value_type = self.infer_expression_type(node.value)
        if symbol["type"] not in {"any", value_type} and value_type != "any":
            raise SemanticError(
                f"Variable '{node.name}' cannot receive a value of type '{value_type}'.",
                node.line,
                node.column,
                "Keep the variable type consistent with its first assignment.",
            )
        if symbol["type"] == "any" and value_type != "any":
            symbol["type"] = value_type
        symbol["initialized"] = True

    def visit_PrintNode(self, node: PrintNode):
        self.infer_expression_type(node.value)

    def visit_ReturnNode(self, node: ReturnNode):
        if self.current_function is None:
            raise SemanticError(
                "Return statements can only be used inside functions.",
                node.line,
                node.column,
                "Move the return statement inside a function block.",
            )
        if node.value is None:
            raise SemanticError(
                f"Function '{self.current_function}' must return a value in version 2.",
                node.line,
                node.column,
                "Use 'return expression;' instead of a bare return.",
            )
        return_type = self.infer_expression_type(node.value)
        signature = self.function_table[self.current_function]
        existing_type = signature["return_type"]
        if existing_type is None:
            signature["return_type"] = return_type
        elif existing_type not in {"any", return_type} and return_type != "any":
            raise SemanticError(
                f"Function '{self.current_function}' returns inconsistent types.",
                node.line,
                node.column,
                "Return the same type from every branch.",
            )

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
        if node.operator in {"<", "<=", ">", ">="}:
            if left_type not in {"int", "any"} or right_type not in {"int", "any"}:
                raise SemanticError(
                    "Order comparisons require numeric expressions.",
                    node.line,
                    node.column,
                    "Use numbers or numeric variables with less/greater comparisons.",
                )
            return
        if left_type != right_type and "any" not in {left_type, right_type}:
            raise SemanticError(
                "Conditions must compare matching value types.",
                node.line,
                node.column,
                "Compare values of the same type.",
            )

    def infer_expression_type(self, node, allow_string: bool = False) -> str:
        if isinstance(node, NumberNode):
            return "int"
        if isinstance(node, StringNode):
            return "string"
        if isinstance(node, IdentifierNode):
            symbol = self.require_symbol(node.name, node.line, node.column)
            return symbol["type"]
        if isinstance(node, CallNode):
            if node.name not in self.function_table:
                raise SemanticError(
                    f"Function '{node.name}' is not declared.",
                    node.line,
                    node.column,
                    "Define the function before calling it.",
                )
            signature = self.function_table[node.name]
            if len(node.args) != len(signature["params"]):
                raise SemanticError(
                    f"Function '{node.name}' expects {len(signature['params'])} argument(s).",
                    node.line,
                    node.column,
                    "Pass the same number of arguments as parameters.",
                )
            for arg in node.args:
                self.infer_expression_type(arg)
            return signature["return_type"] or "any"
        if isinstance(node, BinaryOpNode):
            left_type = self.infer_expression_type(node.left)
            right_type = self.infer_expression_type(node.right)
            if node.operator == "+":
                if left_type == right_type == "string":
                    return "string"
                if left_type in {"int", "any"} and right_type in {"int", "any"}:
                    return "int" if "any" not in {left_type, right_type} else "any"
                if "any" in {left_type, right_type}:
                    return "any"
                raise SemanticError(
                    "The '+' operator requires either two numbers or two strings.",
                    node.line,
                    node.column,
                    "Use matching types on both sides of '+'.",
                )
            if left_type not in {"int", "any"} or right_type not in {"int", "any"}:
                raise SemanticError(
                    "Arithmetic expressions must use numeric values.",
                    node.line,
                    node.column,
                    "Use integers or numeric variables here.",
                )
            return "int" if "any" not in {left_type, right_type} else "any"
        if isinstance(node, ConditionNode):
            self.visit_ConditionNode(node)
            return "bool"
        raise ValueError(f"Unhandled node type {node.__class__.__name__}")

    def require_symbol(self, name: str, line: int, column: int) -> dict:
        for scope in reversed(self.scopes):
            if name in scope:
                symbol = scope[name]
                if not symbol.get("initialized", False):
                    raise SemanticError(
                        f"Variable '{name}' is used before initialization.",
                        line,
                        column,
                        "Assign a value before using the variable.",
                    )
                return symbol
        raise SemanticError(
            f"Variable '{name}' is used before declaration.",
            line,
            column,
            "Declare the variable first using 'declare variable name;'.",
        )

    def lookup_symbol(self, name: str, line: int, column: int) -> dict:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(
            f"Variable '{name}' is used before declaration.",
            line,
            column,
            "Declare the variable first using 'declare variable name;'.",
        )

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def current_scope(self) -> dict[str, dict]:
        return self.scopes[-1]

    def body_contains_return(self, body: list) -> bool:
        for statement in body:
            if isinstance(statement, ReturnNode):
                return True
            if isinstance(statement, IfNode):
                if self.body_contains_return(statement.then_body) or self.body_contains_return(statement.else_body):
                    return True
            if isinstance(statement, WhileNode):
                if self.body_contains_return(statement.body):
                    return True
        return False
