import pydprobe
import pytest
import asyncio

def baz(a, b):
    print(f"baz({a}, {b})")


def bar(a, b, n1 = "asdf", n2 = "fdsa"):
    print("Bar start")
    baz(b, a)
    print("Bar end")

trace_list = []

def trace_callback(func, func_name: str, args: dict):
    global trace_list
    arg_str = [f"{name} = {repr(value)}" for name, value in args.items()]
    trace_list.append(f"OUTPUT: {func_name}({', '.join(arg_str)})")

def test_instrumentation():
    global trace_list
    trace_list = []
    pydprobe.set_trace_callback(trace_callback)
    pydprobe.add_trace("tests.test_instrument", "bar")
    pydprobe.add_trace("tests.test_instrument", "baz")
    bar(1, 2, n2="val")
    assert trace_list == ["OUTPUT: bar(a = 1, b = 2, n1 = 'asdf', n2 = 'val')", 'OUTPUT: baz(a = 2, b = 1)']
    assert set(pydprobe.get_all_traces()) == {"tests.test_instrument.bar", "tests.test_instrument.baz"}
    
    pydprobe.remove_trace("tests.test_instrument", "baz")
    assert set(pydprobe.get_all_traces()) == {"tests.test_instrument.bar"}
    trace_list = []
    bar(1, 2, n2="val")
    assert trace_list == ["OUTPUT: bar(a = 1, b = 2, n1 = 'asdf', n2 = 'val')"]
    
    pydprobe.remove_all_traces()
    assert set(pydprobe.get_all_traces()) == set()
    trace_list = []
    bar(1, 2, n2="val")
    assert trace_list == []
    


self_mod_init = False

def self_mod():
    global self_mod_init
    if not self_mod_init:
        self_mod_init = True
        pydprobe.add_trace("tests.test_instrument", "self_mod")
        self_mod()


def test_self_mod():
    global trace_list
    trace_list = []
    pydprobe.set_trace_callback(trace_callback)
    with pytest.raises(Exception):
        self_mod()


async def async_sleep_func():
    await asyncio.sleep(.2)
    await asyncio.sleep(.2)
    await asyncio.sleep(.2)
    return 2

@pytest.mark.asyncio
async def test_async():
    global trace_list
    trace_list = []
    task = asyncio.create_task(async_sleep_func())
    await asyncio.sleep(.2)
    pydprobe.set_trace_callback(trace_callback)
    with pytest.raises(Exception):
        pydprobe.add_trace("tests.test_instrument", "async_sleep_func")
    await task
    pydprobe.remove_all_traces()
