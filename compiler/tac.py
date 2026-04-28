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


class TACGenerator:
    def __init__(self):
        self.instructions: list[str] = []
        self.temp_counter = 0
        self.label_counter = 0

    def generate(self, program: ProgramNode) -> list[str]:
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0
        for statement in program.statements:
            self.emit_statement(statement)
        return self.instructions

    def emit_statement(self, node):
        method = getattr(self, f"emit_{node.__class__.__name__}", None)
        if not method:
            raise ValueError(f"No TAC emitter for {node.__class__.__name__}")
        method(node)

    def emit_FunctionDefNode(self, node: FunctionDefNode):
        self.instructions.append(f"function {node.name}({', '.join(node.params)}):")
        for statement in node.body:
            self.emit_statement(statement)
        self.instructions.append(f"end function {node.name}")

    def emit_DeclarationNode(self, node: DeclarationNode):
        if node.value is not None:
            value = self.emit_expression(node.value)
            self.instructions.append(f"{node.name} = {value}")

    def emit_AssignmentNode(self, node: AssignmentNode):
        value = self.emit_expression(node.value)
        self.instructions.append(f"{node.name} = {value}")

    def emit_PrintNode(self, node: PrintNode):
        value = self.emit_expression(node.value)
        self.instructions.append(f"print {value}")

    def emit_ReturnNode(self, node: ReturnNode):
        if node.value is None:
            self.instructions.append("return")
            return
        value = self.emit_expression(node.value)
        self.instructions.append(f"return {value}")

    def emit_IfNode(self, node: IfNode):
        else_label = self.new_label()
        end_label = self.new_label()
        condition = self.emit_condition(node.condition)
        self.instructions.append(f"ifFalse {condition} goto {else_label}")
        for statement in node.then_body:
            self.emit_statement(statement)
        if node.else_body:
            self.instructions.append(f"goto {end_label}")
            self.instructions.append(f"{else_label}:")
            for statement in node.else_body:
                self.emit_statement(statement)
            self.instructions.append(f"{end_label}:")
        else:
            self.instructions.append(f"{else_label}:")

    def emit_WhileNode(self, node: WhileNode):
        start_label = self.new_label()
        end_label = self.new_label()
        self.instructions.append(f"{start_label}:")
        condition = self.emit_condition(node.condition)
        self.instructions.append(f"ifFalse {condition} goto {end_label}")
        for statement in node.body:
            self.emit_statement(statement)
        self.instructions.append(f"goto {start_label}")
        self.instructions.append(f"{end_label}:")

    def emit_expression(self, node) -> str:
        if isinstance(node, NumberNode):
            return str(node.value)
        if isinstance(node, StringNode):
            return f"\"{node.value}\""
        if isinstance(node, IdentifierNode):
            return node.name
        if isinstance(node, CallNode):
            args = ", ".join(self.emit_expression(arg) for arg in node.args)
            temp = self.new_temp()
            self.instructions.append(f"{temp} = call {node.name}({args})")
            return temp
        if isinstance(node, BinaryOpNode):
            left = self.emit_expression(node.left)
            right = self.emit_expression(node.right)
            temp = self.new_temp()
            self.instructions.append(f"{temp} = {left} {node.operator} {right}")
            return temp
        raise ValueError(f"Unsupported expression node {node.__class__.__name__}")

    def emit_condition(self, node: ConditionNode) -> str:
        left = self.emit_expression(node.left)
        right = self.emit_expression(node.right)
        return f"{left} {node.operator} {right}"

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"
