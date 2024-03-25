import pydprobe
import pytest
from pydprobe import parser

foo_asdf = 5
bar_asdf = 7

def my_func():
    print("Hello")

trace_list = []

def trace_callback(func, func_name: str, args: dict):
    global trace_list
    arg_str = [f"{name} = {repr(value)}" for name, value in args.items()]
    trace_list.append(f"OUTPUT: {func_name}({', '.join(arg_str)})")

def test_eval():
    vals = parser.eval_exp("foo_asdf")
    assert vals == [('tests.test_parser.foo_asdf', 5)]
    vals = parser.eval_exp("tests.test_parser.foo_asdf")
    assert vals == [('tests.test_parser.foo_asdf', 5)]
    vals = parser.eval_exp("tests.test_parser.*_asdf")
    assert set(vals) == {('tests.test_parser.foo_asdf', 5), ('tests.test_parser.bar_asdf', 7)}

def test_parser_eval():
    result = parser.run_command("eval tests.test_parser.foo_asdf")
    assert result == "tests.test_parser.foo_asdf == 5"

def test_parser_trace():
    global trace_list
    pydprobe.set_trace_callback(trace_callback)
    result = parser.run_command("trace my_func")
    assert result == "Tracing functions:\ntests.test_parser.my_func"
    my_func()
    assert trace_list == ["OUTPUT: my_func()"]
    result = parser.run_command("traces")
    assert result == "Currently traced functions:\ntests.test_parser.my_func"

    result = parser.run_command("untrace my_func")  
    trace_list = []
    my_func()
    assert trace_list == []

