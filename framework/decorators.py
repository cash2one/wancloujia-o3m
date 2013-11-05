import time
from functools import wraps

from django.utils import simplejson
from django.http import HttpResponse
from django.contrib import auth

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


def check_login(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return simplejson.dumps({'ret_code': 1001})
        return func(request, *args, **kwargs)
    return wrapper

def response_error(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        return simplejson.dumps({'ret_code': 1000, 'ret_msg': 'Easy. Just for test:)'})
    return wrapper

