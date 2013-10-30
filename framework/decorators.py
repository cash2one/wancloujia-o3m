import time
from functools import wraps

def request_delay(secs):
    def outer_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            time.sleep(secs)
            return func(*args, **kwargs)
        return wrapper
    return outer_wrapper

