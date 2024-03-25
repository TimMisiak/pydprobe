import sys

def get_module_by_name(module_name: str):
    if sys.modules["__main__"].__spec__.name == module_name:
        module = sys.modules.get("__main__")
    else:
        module = sys.modules.get(module_name)
    return module