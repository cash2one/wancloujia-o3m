import logging

from django.contrib import auth
from django.utils import simplejson
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from suning.decorators import active_tab

logger = logging.getLogger(__name__)


@require_GET
def welcome(request):
    if request.user.is_authenticated():
        return redirect("/mgr/account/")
    else:
        return render(request, "login.html") 


@require_GET
@login_required
def logout(request):
    auth.logout(request)
    return redirect("/welcome")


@require_GET
@login_required
def permission_denied(request):
    return render(request, "permission_denied.html")


def welcome_json(request):
    return HttpResponse(simplejson.dumps({'ret_code': 1000, 'ret_msg': 'not_login_error'}), 
                        mimetype='application/json')


def permission_denied_json(request):
    return HttpResponse(simplejson.dumps({'ret_code': 1000, 'ret_msg': 'permission_denied'}), 
                        mimetype='application/json')
