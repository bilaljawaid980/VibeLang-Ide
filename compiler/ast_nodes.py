from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Node:
    line: int
    column: int

    def to_dict(self) -> dict:
        data = {"type": self.__class__.__name__, "line": self.line, "column": self.column}
        for key, value in self.__dict__.items():
            if key in {"line", "column"}:
                continue
            if isinstance(value, list):
                data[key] = [item.to_dict() if isinstance(item, Node) else item for item in value]
            elif isinstance(value, Node):
                data[key] = value.to_dict()
            else:
                data[key] = value
        return data


@dataclass
class ProgramNode(Node):
    statements: list[Node] = field(default_factory=list)


@dataclass
class FunctionDefNode(Node):
    name: str
    params: list[str] = field(default_factory=list)
    body: list[Node] = field(default_factory=list)


@dataclass
class DeclarationNode(Node):
    name: str
    value: Optional[Node] = None


@dataclass
class AssignmentNode(Node):
    name: str
    value: Node


@dataclass
class PrintNode(Node):
    value: Node


@dataclass
class ReturnNode(Node):
    value: Optional[Node] = None


@dataclass
class IfNode(Node):
    condition: Node
    then_body: list[Node]
    else_body: list[Node] = field(default_factory=list)


@dataclass
class WhileNode(Node):
    condition: Node
    body: list[Node]


@dataclass
class BinaryOpNode(Node):
    operator: str
    left: Node
    right: Node


@dataclass
class NumberNode(Node):
    value: int


@dataclass
class StringNode(Node):
    value: str


@dataclass
class IdentifierNode(Node):
    name: str


@dataclass
class CallNode(Node):
    name: str
    args: list[Node] = field(default_factory=list)


@dataclass
class ConditionNode(Node):
    operator: str
    left: Node
    right: Node
