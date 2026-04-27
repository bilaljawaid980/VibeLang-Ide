from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.errors import SyntaxError


def test_parser_accepts_valid_if_statement():
    source = "if x is less than 10 then print x; end if;"
    tokens = Lexer().tokenize(source)
    ast = Parser(tokens).parse()
    assert len(ast.statements) == 1


def test_parser_rejects_missing_then():
    source = "if x is less than 10 print x; end if;"
    tokens = Lexer().tokenize(source)
    try:
        Parser(tokens).parse()
    except SyntaxError as error:
        assert "then" in error.message.lower()
    else:
        raise AssertionError("Expected syntax error for missing then.")
