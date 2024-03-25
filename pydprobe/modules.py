import sys
import inspect

def get_module_by_name(module_name: str):
    if sys.modules["__main__"].__spec__.name == module_name:
        module = sys.modules.get("__main__")
    else:
        module = sys.modules.get(module_name)
    return module


def get_function_name(func: callable):
    mod_name = inspect.getmodule(func).__name__
    func_name = func.__name__
    return f"{mod_name}.{func_name}"