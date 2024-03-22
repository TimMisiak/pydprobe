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

def trace_callback(func_name: str, args: dict):
    global trace_list
    arg_str = [f"{name} = {repr(value)}" for name, value in args.items()]
    trace_list.append(f"OUTPUT: {func_name}({', '.join(arg_str)})")

def test_instrumentation():
    global trace_list
    trace_list = []
    pydprobe.set_trace_callback(trace_callback)
    pydprobe.add_trace("tests.test_basics", "bar")
    pydprobe.add_trace("tests.test_basics", "baz")
    bar(1, 2, n2="val")
    assert trace_list == ["OUTPUT: bar(a = 1, b = 2, n1 = 'asdf', n2 = 'val')", 'OUTPUT: baz(a = 2, b = 1)']


self_mod_init = False

def self_mod():
    global self_mod_init
    if not self_mod_init:
        self_mod_init = True
        pydprobe.add_trace("tests.test_basics", "self_mod")
        self_mod()


def test_self_mod():
    global trace_list
    trace_list = []
    pydprobe.set_trace_callback(trace_callback)
    with pytest.raises(Exception):
        self_mod()


async def async_sleep_func():
    await asyncio.sleep(1)
    await asyncio.sleep(1)
    await asyncio.sleep(1)
    return 2

@pytest.mark.asyncio
async def test_async():
    global trace_list
    trace_list = []
    task = asyncio.create_task(async_sleep_func())
    await asyncio.sleep(1)
    pydprobe.set_trace_callback(trace_callback)
    pydprobe.add_trace("tests.test_basics", "async_sleep_func")
    task2 = asyncio.create_task(async_sleep_func())
    ret = await task
    assert ret == 2
    await task2
    assert trace_list == ['OUTPUT: async_sleep_func()']
