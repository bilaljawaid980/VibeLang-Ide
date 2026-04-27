from __future__ import annotations

from .errors import CompilerError
from .interpreter import Interpreter
from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .tac import TACGenerator


def compile_source(source_code: str) -> dict:
    lexer = Lexer()
    try:
        tokens = lexer.tokenize(source_code)
        parser = Parser(tokens)
        ast = parser.parse()
        semantic = SemanticAnalyzer()
        symbol_table = semantic.analyze(ast)
        tac_generator = TACGenerator()
        tac = tac_generator.generate(ast)
        interpreter = Interpreter()
        runtime_output = interpreter.execute(ast)
        return {
            "success": True,
            "tokens": [token.to_dict() for token in tokens if token.type != "EOF"],
            "token_display": [token.display() for token in tokens if token.type != "EOF"],
            "ast": ast.to_dict(),
            "symbol_table": symbol_table,
            "semantic_errors": [],
            "tac": tac,
            "runtime_output": runtime_output,
            "errors": [],
        }
    except CompilerError as error:
        return {
            "success": False,
            "tokens": [token.to_dict() for token in locals().get("tokens", []) if token.type != "EOF"],
            "token_display": [token.display() for token in locals().get("tokens", []) if token.type != "EOF"],
            "ast": None,
            "symbol_table": {},
            "semantic_errors": [error.to_dict()] if error.error_type == "SemanticError" else [],
            "tac": [],
            "runtime_output": [],
            "errors": [error.to_dict()],
        }
