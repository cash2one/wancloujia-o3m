# coding: utf-8

from django.utils import simplejson
from django.http import HttpResponse

def render_json(obj):
    return HttpResponse(simplejson.dumps(obj), mimetype='application/json')

