from compiler.lexer import Lexer


def test_lexer_tokenizes_basic_program():
    tokens = Lexer().tokenize('declare variable x = 10;\nprint "hello";')
    token_types = [token.type for token in tokens]
    assert token_types == [
        "DECLARE",
        "VARIABLE",
        "ID",
        "ASSIGN",
        "NUMBER",
        "SEMICOLON",
        "PRINT",
        "STRING",
        "SEMICOLON",
        "EOF",
    ]
