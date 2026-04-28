from compiler.compiler import compile_source


def test_v2_supports_string_variables_and_concatenation():
    source = """
declare variable title = "Vibe";
title = title + "Lang";
print title;
""".strip()

    result = compile_source(source)

    assert result["success"] is True
    assert result["runtime_output"] == ["VibeLang"]


def test_v2_supports_functions_and_calls():
    source = """
function greet(name) then
    return "Hello, " + name;
end function;
declare variable message = greet("Ali");
print message;
""".strip()

    result = compile_source(source)

    assert result["success"] is True
    assert result["runtime_output"] == ["Hello, Ali"]
    assert any("call greet" in instruction for instruction in result["tac"])
