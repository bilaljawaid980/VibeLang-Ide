from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CompilerError(Exception):
    error_type: str
    message: str
    line: int
    column: int
    hint: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "type": self.error_type,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "hint": self.hint,
        }


class LexicalError(CompilerError):
    def __init__(self, message: str, line: int, column: int, hint: Optional[str] = None):
        super().__init__("LexicalError", message, line, column, hint)


class SyntaxError(CompilerError):
    def __init__(self, message: str, line: int, column: int, hint: Optional[str] = None):
        super().__init__("SyntaxError", message, line, column, hint)


class SemanticError(CompilerError):
    def __init__(self, message: str, line: int, column: int, hint: Optional[str] = None):
        super().__init__("SemanticError", message, line, column, hint)


class RuntimeError(CompilerError):
    def __init__(self, message: str, line: int, column: int, hint: Optional[str] = None):
        super().__init__("RuntimeError", message, line, column, hint)
