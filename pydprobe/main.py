import dis
import types
import inspect
from . import test, instrument

def baz(a, b):
    print(f"baz({a}, {b})")


def bar(a, b, n1 = "asdf", n2 = "fdsa"):
    print("Bar start")
    baz(b, a)
    print("Bar end")

def trace_callback(func_name: str, args: dict):
    arg_str = [f"{name} = {repr(value)}" for name, value in args.items()]
    print(f"TRACE2: {func_name}({', '.join(arg_str)})")

if __name__ == "__main__":
    instrument.set_trace_callback(trace_callback)
    instrument.add_trace("pydprobe.main", "bar")
    instrument.add_trace("pydprobe.main", "baz")
    bar(1, 2, n2="val")