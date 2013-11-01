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

def active_tab(tab, sub_tab=None):
    def outer_wrapper(func):
        @wraps(func)
        def wrapper(request):
            request.nav = request.nav if hasattr(request, "nav") else {}
            request.nav["active_tab"] = tab
            if sub_tab is not None:
                request.nav["sub_active_tab"] = sub_tab
            return func(request)
        return wrapper
    return outer_wrapper

