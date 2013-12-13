# coding: utf-8

from django.utils import simplejson
from django.http import HttpResponse

def render_json(obj):
    return HttpResponse(simplejson.dumps(obj), mimetype='application/json')


def first_valid(test, items, default=None):
    for item in items:
        if test(item):
            return item

    return default


def get_model_by_pk(manager, pk, default=None):
    data = manager.filter(pk=pk)
    return data[0] if data else default

