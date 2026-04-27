from __future__ import annotations

import re
from dataclasses import dataclass

from .errors import LexicalError


KEYWORDS = {
    "declare": "DECLARE",
    "variable": "VARIABLE",
    "if": "IF",
    "then": "THEN",
    "else": "ELSE",
    "end": "END",
    "while": "WHILE",
    "do": "DO",
    "print": "PRINT",
    "is": "IS",
    "less": "LESS",
    "greater": "GREATER",
    "than": "THAN",
    "equal": "EQUAL",
    "to": "TO",
    "not": "NOT",
    "or": "OR",
}

SINGLE_CHAR_TOKENS = {
    "=": "ASSIGN",
    "+": "PLUS",
    "-": "MINUS",
    "*": "TIMES",
    "/": "DIVIDE",
    ";": "SEMICOLON",
    "(": "LPAREN",
    ")": "RPAREN",
}

IDENTIFIER_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")
NUMBER_RE = re.compile(r"\d+")


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "value": self.value,
            "line": self.line,
            "column": self.column,
        }

    def display(self) -> str:
        if self.type in {"ID", "NUMBER", "STRING"}:
            return f"{self.type}({self.value})"
        return self.type


class Lexer:
    def tokenize(self, source_code: str) -> list[Token]:
        tokens: list[Token] = []
        index = 0
        line = 1
        column = 1
        length = len(source_code)

        while index < length:
            char = source_code[index]

            if char in " \t\r":
                index += 1
                column += 1
                continue

            if char == "\n":
                index += 1
                line += 1
                column = 1
                continue

            if char == '"':
                start_col = column
                index += 1
                column += 1
                string_chars: list[str] = []
                while index < length and source_code[index] != '"':
                    if source_code[index] == "\n":
                        raise LexicalError(
                            "Unterminated string literal.",
                            line,
                            start_col,
                            "Close the string with a double quote on the same line.",
                        )
                    string_chars.append(source_code[index])
                    index += 1
                    column += 1
                if index >= length:
                    raise LexicalError(
                        "Unterminated string literal.",
                        line,
                        start_col,
                        "Close the string with a double quote.",
                    )
                index += 1
                column += 1
                tokens.append(Token("STRING", "".join(string_chars), line, start_col))
                continue

            if char in SINGLE_CHAR_TOKENS:
                tokens.append(Token(SINGLE_CHAR_TOKENS[char], char, line, column))
                index += 1
                column += 1
                continue

            identifier_match = IDENTIFIER_RE.match(source_code, index)
            if identifier_match:
                value = identifier_match.group(0)
                token_type = KEYWORDS.get(value.lower(), "ID")
                tokens.append(Token(token_type, value, line, column))
                advance = len(value)
                index += advance
                column += advance
                continue

            number_match = NUMBER_RE.match(source_code, index)
            if number_match:
                value = number_match.group(0)
                tokens.append(Token("NUMBER", value, line, column))
                advance = len(value)
                index += advance
                column += advance
                continue

            raise LexicalError(
                f"Unexpected character '{char}'.",
                line,
                column,
                "Remove the character or replace it with supported VibeLang syntax.",
            )

        tokens.append(Token("EOF", "", line, column))
        return tokens
