from typing import Callable
from . import instrument, modules
import fnmatch
import sys

def recursive_eval(obj, parts, parent_name):
    if parts == []:
        return [(parent_name, obj)]
    part = parts[0]
    children = [x for x in obj.__dict__.keys() if fnmatch.fnmatch(x, part)]
    ret = []
    for child_name in children:
        full_name = f"{parent_name}.{child_name}"
        child_obj = getattr(obj, child_name)
        ret.extend(recursive_eval(child_obj, parts[1:], full_name))
    return ret

def eval_exp(exp: str):
    parts = exp.split('.')
    # First try to find an explicit module match
    ret = set()
    found_module = False
    for i in range(1, len(parts)):
        mod_parts = parts[:i]
        mod_name = ".".join(mod_parts)
        module = modules.get_module_by_name(mod_name)
        if module:
            found_module = True
            ret = ret.union(recursive_eval(module, parts[i:], mod_name))
    # If we don't find a module match, try to evaluate this against all modules in the main package. Potentially slow? Maybe we can put some filter to make sure we're not trying to eval
    # stuff in imported packages
    if not found_module:
        for mod_name, mod in sys.modules.items():
            ret = ret.union(recursive_eval(mod, parts, mod_name))
    return list(ret)

def run_trace(cmd: str):
    vals = eval_exp(cmd)
    if len(vals) == 0:
        return "Error: function not found"
    ret = []
    for name, val in vals:
        if callable(val):
            instrument.add_trace_func(val)
            ret.append(name)
    if len(ret) == 0:
        return "Error: Expression did not evaluate to any function"
    return "Tracing functions:\n" + "\n".join(ret)

def run_traces(cmd: str):
    if cmd.strip() != "":
        return "Error: No parameters expected for 'traces' command"
    traced_funcs = instrument.get_all_traces()
    return "Currently traced functions:\n" + "\n".join(traced_funcs)

def run_untrace(cmd: str):
    if cmd.strip() == "":
        instrument.remove_all_traces()
        return "All functions untraced"
    vals = eval_exp(cmd)
    ret = []
    for name, val in vals:
        if instrument.remove_trace_func(val):
            ret.append(name)
    if len(ret) == 0:
        return "Error: Expression did not match any traced functions"
    return "Untraced functions:\n" + "\n".join(ret)

def run_eval(cmd: str):
    vals = eval_exp(cmd)
    ret = []
    for name, val in vals:
        ret.append(f"{name} == {repr(val)}")
    if len(ret) == 0:
        return "Error: Expression did not match any values"
    return "\n".join(ret)

commands = [
    ("trace", run_trace),
    ("traces", run_traces),
    ("untrace", run_untrace),
    ("eval", run_eval),
]

def run_command(cmd: str):
    for (prefix, func) in commands:
        if cmd.startswith(f"{prefix} "):
            return func(cmd[len(prefix) + 1:])
        if cmd == prefix:
            return func("")
    return "Error: Unrecognized command"