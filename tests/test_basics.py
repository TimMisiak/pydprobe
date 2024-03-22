from pydprobe import instrument

def baz(a, b):
    print(f"baz({a}, {b})")


def bar(a, b, n1 = "asdf", n2 = "fdsa"):
    print("Bar start")
    baz(b, a)
    print("Bar end")

trace_list = []

def trace_callback(func_name: str, args: dict):
    global trace_list
    arg_str = [f"{name} = {repr(value)}" for name, value in args.items()]
    trace_list.append(f"OUTPUT: {func_name}({', '.join(arg_str)})")

def test_instrumentation():
    global trace_list
    trace_list = []
    instrument.set_trace_callback(trace_callback)
    instrument.add_trace("tests.test_basics", "bar")
    instrument.add_trace("tests.test_basics", "baz")
    bar(1, 2, n2="val")
    assert trace_list == ["OUTPUT: bar(a = 1, b = 2, n1 = 'asdf', n2 = 'val')", 'OUTPUT: baz(a = 2, b = 1)']
