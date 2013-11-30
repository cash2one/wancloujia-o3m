# coding: utf-8
import logging
from time import sleep
from django.utils import simplejson
from django.contrib import auth
from dajaxice.decorators import dajaxice_register
from auth_remember import remember_user
from forms import LoginForm

logger = logging.getLogger(__name__)

@dajaxice_register(method='POST')
def login(request, username, password, remember_me):
    logger.debug("login: username: %s;password: %s" % (username, password))
    form = LoginForm({'username': username, 'password': password})
    if not form.is_valid():
        logger.debug("form is invalid")    
        logger.warn(form.errors)
        return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'用户名或密码格式不正确！'})

    data = form.cleaned_data
    logger.debug("username: %s; password: %s" % (data['username'], data['password']))
    user = auth.authenticate(username=data['username'], password=data['password'])
    if user is None:
        logger.debug("user is not authenticated")
        return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'用户名或密码不正确！'})

    if not user.is_active:
        logger.debug("user is not active")
        return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'账号被锁定，登录失败！'})

    logger.debug("user is authenticated")
    auth.login(request, user)
    if remember_me:
        remember_user(request, user)

    return simplejson.dumps({'ret_code': 0})

