from functools import wraps


def my_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Begin wrapped")
        ret = func(*args, **kwargs)
        print("End wrapped")
        return ret
    return wrapper