#coding: utf-8
import logging
import time
from functools import wraps

from django.utils import simplejson
from django.http import HttpResponse
from django.contrib import auth
from dajaxice.utils import deserialize_form
from oplog.models import op_log

logger = logging.getLogger(__name__)

def preprocess_form(func):
    @wraps(func)
    def wrap(request, *args, **kwargs):
        f = kwargs["form"]
        form = deserialize_form(f)
        dict = map(lambda k: (k, form[k]), form)
        logger.debug("form:")
        for k, v in dict:
            logger.debug("%s: %s %s", k, v, type(v))

        return func(request, form=form)
    return wrap


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


def oplogtrack(type, username, model = None):
    #import ipdb;ipdb.set_trace()
    log = op_log()
    log.username = username
    if model:
        if model.__unicode__:
            log.content = u'%s(%s)' % (type, model.__unicode__(),)
        elif model.__str__:
            log.content = u'%s(%s)' % (type, model.__str__(),)
    else:
        log.content = u'%s' % (type,)
    log.type = 0
    log.save()