from compiler.compiler import compile_source


def test_semantic_rejects_undeclared_variable():
    result = compile_source("x = 10;")
    assert result["success"] is False
    assert result["errors"][0]["type"] == "SemanticError"
