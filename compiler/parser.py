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
from .errors import SyntaxError
from .lexer import Token


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    def parse(self) -> ProgramNode:
        statements = self.parse_statement_list(stop_tokens={"EOF"})
        self.expect("EOF")
        first_token = self.tokens[0] if self.tokens else Token("EOF", "", 1, 1)
        return ProgramNode(line=first_token.line, column=first_token.column, statements=statements)

    def parse_statement_list(self, stop_tokens: set[str]) -> list:
        statements = []
        while self.current().type not in stop_tokens:
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        token_type = self.current().type
        if token_type == "DECLARE":
            return self.parse_declaration()
        if token_type == "ID":
            return self.parse_assignment()
        if token_type == "PRINT":
            return self.parse_print()
        if token_type == "IF":
            return self.parse_if()
        if token_type == "WHILE":
            return self.parse_while()
        token = self.current()
        raise SyntaxError(
            f"Unexpected token '{token.value or token.type}'.",
            token.line,
            token.column,
            "Start the line with declare, print, if, while, or an identifier assignment.",
        )

    def parse_declaration(self) -> DeclarationNode:
        start = self.expect("DECLARE")
        self.expect("VARIABLE")
        identifier = self.expect("ID")
        value = None
        if self.match("ASSIGN"):
            value = self.parse_expression()
        self.expect("SEMICOLON", "Expected ';' after declaration.", "Add ';' at the end of the declaration.")
        return DeclarationNode(line=start.line, column=start.column, name=identifier.value, value=value)

    def parse_assignment(self) -> AssignmentNode:
        identifier = self.expect("ID")
        self.expect("ASSIGN", "Expected '=' in assignment.", "Use '=' between the variable name and expression.")
        value = self.parse_expression()
        self.expect("SEMICOLON", "Expected ';' after assignment.", "Add ';' at the end of the assignment.")
        return AssignmentNode(line=identifier.line, column=identifier.column, name=identifier.value, value=value)

    def parse_print(self) -> PrintNode:
        start = self.expect("PRINT")
        value = self.parse_expression()
        self.expect("SEMICOLON", "Expected ';' after print statement.", "Add ';' at the end of the print statement.")
        return PrintNode(line=start.line, column=start.column, value=value)

    def parse_if(self) -> IfNode:
        start = self.expect("IF")
        condition = self.parse_condition()
        self.expect("THEN", "Expected 'then' after condition.", "Add 'then' before the if-body.")
        then_body = self.parse_statement_list(stop_tokens={"ELSE", "END"})
        else_body = []
        if self.match("ELSE"):
            else_body = self.parse_statement_list(stop_tokens={"END"})
        self.expect("END", "Expected 'end' to close if block.", "Close the block with 'end if;'.")
        self.expect("IF", "Expected 'if' after 'end'.", "Close the block with 'end if;'.")
        self.expect("SEMICOLON", "Expected ';' after 'end if'.", "Close the block with 'end if;'.")
        return IfNode(line=start.line, column=start.column, condition=condition, then_body=then_body, else_body=else_body)

    def parse_while(self) -> WhileNode:
        start = self.expect("WHILE")
        condition = self.parse_condition()
        self.expect("DO", "Expected 'do' after while condition.", "Add 'do' before the while-body.")
        body = self.parse_statement_list(stop_tokens={"END"})
        self.expect("END", "Expected 'end' to close while block.", "Close the block with 'end while;'.")
        self.expect("WHILE", "Expected 'while' after 'end'.", "Close the block with 'end while;'.")
        self.expect("SEMICOLON", "Expected ';' after 'end while'.", "Close the block with 'end while;'.")
        return WhileNode(line=start.line, column=start.column, condition=condition, body=body)

    def parse_condition(self) -> ConditionNode:
        left = self.parse_expression()
        operator = self.parse_english_relop()
        right = self.parse_expression()
        return ConditionNode(line=left.line, column=left.column, operator=operator, left=left, right=right)

    def parse_english_relop(self) -> str:
        start = self.expect("IS", "Expected relational phrase starting with 'is'.", "Use forms like 'is less than'.")
        if self.match("LESS"):
            self.expect("THAN")
            if self.match("OR"):
                self.expect("EQUAL")
                self.expect("TO")
                return "<="
            return "<"
        if self.match("GREATER"):
            self.expect("THAN")
            if self.match("OR"):
                self.expect("EQUAL")
                self.expect("TO")
                return ">="
            return ">"
        if self.match("EQUAL"):
            self.expect("TO")
            return "=="
        if self.match("NOT"):
            self.expect("EQUAL")
            self.expect("TO")
            return "!="
        raise SyntaxError(
            "Invalid relational operator.",
            start.line,
            start.column,
            "Use 'is less than', 'is greater than', 'is equal to', or 'is not equal to'.",
        )

    def parse_expression(self):
        node = self.parse_term()
        while self.current().type in {"PLUS", "MINUS"}:
            operator = self.advance().value
            right = self.parse_term()
            node = BinaryOpNode(line=node.line, column=node.column, operator=operator, left=node, right=right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current().type in {"TIMES", "DIVIDE"}:
            operator = self.advance().value
            right = self.parse_factor()
            node = BinaryOpNode(line=node.line, column=node.column, operator=operator, left=node, right=right)
        return node

    def parse_factor(self):
        token = self.current()
        if token.type == "NUMBER":
            self.advance()
            return NumberNode(line=token.line, column=token.column, value=int(token.value))
        if token.type == "STRING":
            self.advance()
            return StringNode(line=token.line, column=token.column, value=token.value)
        if token.type == "ID":
            self.advance()
            return IdentifierNode(line=token.line, column=token.column, name=token.value)
        if token.type == "LPAREN":
            self.advance()
            expression = self.parse_expression()
            self.expect("RPAREN", "Expected ')' after expression.", "Close the grouped expression with ')'.")
            return expression
        raise SyntaxError(
            f"Unexpected token '{token.value or token.type}' in expression.",
            token.line,
            token.column,
            "Use a number, string, identifier, or parenthesized expression here.",
        )

    def current(self) -> Token:
        return self.tokens[self.position]

    def advance(self) -> Token:
        token = self.tokens[self.position]
        self.position += 1
        return token

    def match(self, token_type: str) -> bool:
        if self.current().type == token_type:
            self.position += 1
            return True
        return False

    def expect(self, token_type: str, message: str | None = None, hint: str | None = None) -> Token:
        token = self.current()
        if token.type != token_type:
            raise SyntaxError(
                message or f"Expected token '{token_type}' but found '{token.value or token.type}'.",
                token.line,
                token.column,
                hint,
            )
        self.position += 1
        return token
