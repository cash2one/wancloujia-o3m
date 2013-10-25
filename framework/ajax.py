# coding: utf-8
from django.utils import simplejson
from django.contrib import auth
from dajaxice.decorators import dajaxice_register

@dajaxice_register(method='POST')
def login(request, username, password):
    user = auth.authenticate(username=username, password=password)
    if user is None:
        return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'用户名或密码不正确！'})

    if not user.is_active:
        return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'账号被锁定，登录失败！'})

    auth.login(request, user)
    return simplejson.dumps({'ret_code': 0})

