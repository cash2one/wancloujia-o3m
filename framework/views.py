# coding: utf-8
import logging

from django.contrib import auth
from django.utils import simplejson
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST

from django_render_json import json as re_json

from forms import LoginForm

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


@require_POST
@re_json
def login(request):
    form = LoginForm(request.POST)
    if not form.is_valid():
        logger.debug("form is invalid")    
        logger.warn(form.errors)
        return {
            'ret_code': 1000, 
            'ret_msg': u'用户名或密码格式不正确！'
        }

    data = form.cleaned_data
    logger.debug("username: %s; password: %s" % (data['username'], data['password']))
    user = auth.authenticate(username=data['username'], password=data['password'])
    if user is None:
        logger.debug("user is not authenticated")
        return {
            'ret_code': 1000, 
            'ret_msg': u'用户名或密码不正确！'
        }

    if not user.is_active:
        logger.debug("user is not active")
        return {
            'ret_code': 1000, 
            'ret_msg': u'账号被锁定，登录失败！'
        }

    logger.debug("user is authenticated")
    auth.login(request, user)
    if remember_me:
        remember_user(request, user)

    return {
        'ret_code': 0
    }
