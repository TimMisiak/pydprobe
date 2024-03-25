import asyncio

def is_event_loop_running():
    try:
        loop = asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False

def is_func_active(func):
    if not is_event_loop_running():
        return False
    for task in asyncio.all_tasks():
        stack = task.get_stack()
        for frame in stack:
            if frame.f_code == func.__code__:
                return True
    return False