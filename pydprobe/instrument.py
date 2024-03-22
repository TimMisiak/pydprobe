import inspect
from typing import Callable
import types
import sys
import platform
from . import threads


def default_trace_callback(func_name: str, args: dict):
    arg_str = [f"{name} = {repr(value)}" for name, value in args.items()]
    print(f"TRACE: {func_name}({', '.join(arg_str)})")

_trace_callback = default_trace_callback

def set_trace_callback(callback: Callable[[str, dict], None]):
    global _trace_callback
    _trace_callback = callback

# Called from the traced function
def __instrument_pre_call():
    # Get the caller's frame
    caller_frame = inspect.currentframe().f_back
    
    # Get function name in the caller's frame
    func_name = caller_frame.f_code.co_name

    # Get the function object from the caller's frame
    caller_func = caller_frame.f_globals[func_name]

    # Get the signature of the function
    sig = inspect.signature(caller_func)

    # Get the arguments in the caller's frame
    args, _, _, values = inspect.getargvalues(caller_frame)

    # Print all arguments, including kwargs
    
    args = []
    arg_dict = {}
    for param in sig.parameters.values():
        name = param.name
        value = values.get(name, param.default)
        arg_dict[name] = value
    if _trace_callback:
        try:
            _trace_callback(func_name, arg_dict)
        except:
            pass

# Used to generate the bytecode that we'll prepend to the traced function
def preamble():
    __instrument_pre_call()

def add_trace(module_name, func_name):
    pyver = platform.python_version_tuple()
    # Old python uses strings in the tuple
    pyver = tuple(int(number) for number in pyver)

    if pyver > (3, 12, 1):
        raise Exception("Current python version is untested. Highest tested is 3.12.1")

    if sys.modules["__main__"].__spec__.name == module_name:
        module = sys.modules["__main__"]
    else:
        module = sys.modules[module_name]
    func = getattr(module, func_name)

    if threads.is_func_active(func):
        raise Exception("Can't instrument an active function")


    setattr(module, "__instrument_pre_call", __instrument_pre_call)
    orig = func.__code__

    # Find the new co_names index
    new_idx = len(orig.co_names)
    new_names = orig.co_names + ("__instrument_pre_call",)

    if pyver < (3, 11, 0):
        # Get just the LOAD_GLOBAL, CALL_FUNCTION, POP_TOP. Should be 6 bytes.
        preamble_code = list(preamble.__code__.co_code)[:6]
        if preamble_code != [116, 0, 131, 0, 1, 0]:
            raise Exception("Unexpected code bytes. Unsupported version of python")
        # Update the LOAD_GLOBAL to reference pre_call in the new names array
        preamble_code[1] = new_idx
        new_bytecode = bytes(preamble_code + list(orig.co_code))
        
    elif pyver >= (3, 11, 0) and pyver < (3, 12, 0):
        preamble_code = list(preamble.__code__.co_code)[:30]
        if preamble_code != [151, 0, 116, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 166, 0, 0, 0, 171, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]:
            raise Exception("Unexpected code bytes. Unsupported version of python")    
        # Update the LOAD_GLOBAL to reference pre_call in the new names array
        preamble_code[3] = new_idx * 2 + 1
        new_bytecode = bytes(preamble_code + list(orig.co_code)[2:])
    else:
        preamble_code = list(preamble.__code__.co_code)[:22]
        print(repr(preamble_code))
        if preamble_code != [151, 0, 116, 1, 0, 0, 0, 0, 0, 0, 0, 0, 171, 0, 0, 0, 0, 0, 0, 0, 1, 0]:
            raise Exception("Unexpected code bytes. Unsupported version of python")    
        # Update the LOAD_GLOBAL to reference pre_call in the new names array
        preamble_code[3] = new_idx * 2 + 1
        new_bytecode = bytes(preamble_code + list(orig.co_code)[2:])

    if pyver >= (3, 6, 0) and pyver < (3, 8, 0):
        new_code = types.CodeType(
            orig.co_argcount,
            orig.co_kwonlyargcount,
            orig.co_nlocals,
            orig.co_stacksize,
            orig.co_flags,
            new_bytecode,
            orig.co_consts,
            new_names,
            orig.co_varnames,
            orig.co_filename,
            orig.co_name,
            orig.co_firstlineno,
            orig.co_lnotab,
            orig.co_freevars,
            orig.co_cellvars
        )
    elif pyver >= (3, 8, 0) and pyver < (3, 10, 0):
        new_code = types.CodeType(
            orig.co_argcount,
            orig.co_posonlyargcount,  # This is supported from Python 3.8 onwards
            orig.co_kwonlyargcount,
            orig.co_nlocals,
            orig.co_stacksize,
            orig.co_flags,
            new_bytecode,
            orig.co_consts,
            new_names,
            orig.co_varnames,
            orig.co_filename,
            orig.co_name,
            orig.co_firstlineno,
            orig.co_lnotab,  # Python 3.8 still uses co_lnotab instead of co_linetable
            orig.co_freevars,
            orig.co_cellvars
        )
    elif pyver >= (3, 10, 0) and pyver < (3, 11, 0):
        new_code = types.CodeType(
            orig.co_argcount,
            orig.co_posonlyargcount,
            orig.co_kwonlyargcount,
            orig.co_nlocals,
            orig.co_stacksize,
            orig.co_flags,
            new_bytecode,
            orig.co_consts,
            new_names,
            orig.co_varnames,
            orig.co_filename,
            orig.co_name,
            orig.co_firstlineno,
            orig.co_linetable,
            orig.co_freevars,
            orig.co_cellvars
        )
    else: # >3.11

        new_code = types.CodeType(
            orig.co_argcount,
            orig.co_posonlyargcount,
            orig.co_kwonlyargcount,
            orig.co_nlocals,
            orig.co_stacksize,
            orig.co_flags,
            new_bytecode,
            orig.co_consts,
            new_names,
            orig.co_varnames,
            orig.co_filename,
            orig.co_name,
            orig.co_qualname,
            orig.co_firstlineno,
            orig.co_linetable,
            orig.co_exceptiontable,  # New in Python 3.11
            orig.co_freevars,
            orig.co_cellvars
        )
    func.__code__ = new_code