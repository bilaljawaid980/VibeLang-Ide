from compiler.compiler import compile_source


def test_compile_returns_runtime_output_for_prints():
    source = """
declare variable counter = 1;
while counter is less than or equal to 3 do
    print counter;
    counter = counter + 1;
end while;
print \"done\";
""".strip()

    result = compile_source(source)

    assert result["success"] is True
    assert result["runtime_output"] == ["1", "2", "3", "done"]


def test_compile_returns_runtime_error_for_division_by_zero():
    source = """
declare variable x = 10;
declare variable y = 0;
print x / y;
""".strip()

    result = compile_source(source)

    assert result["success"] is False
    assert result["errors"][0]["type"] == "RuntimeError"
    assert "Division by zero" in result["errors"][0]["message"]
