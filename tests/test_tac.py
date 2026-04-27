from compiler.compiler import compile_source


def test_tac_generates_control_flow():
    source = """
declare variable counter = 1;
while counter is less than 3 do
    print counter;
    counter = counter + 1;
end while;
""".strip()
    result = compile_source(source)
    assert result["success"] is True
    assert result["tac"] == [
        "counter = 1",
        "L1:",
        "ifFalse counter < 3 goto L2",
        "print counter",
        "t1 = counter + 1",
        "counter = t1",
        "goto L1",
        "L2:",
    ]
