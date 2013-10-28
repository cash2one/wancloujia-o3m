# coding: utf-8
from django.utils import simplejson
from django.contrib import auth
from dajaxice.decorators import dajaxice_register
from auth_remember import remember_user
from forms import LoginForm

@dajaxice_register(method='POST')
def login(request, username, password, remember_me):
    form = LoginForm({'username': username, 'password': password})
    if not form.is_valid():
        return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'用户名或密码不正确！'})

    data = form.cleaned_data
    user = auth.authenticate(username=data['username'], password=data['password'])
    if user is None:
        return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'用户名或密码不正确！'})

    if not user.is_active:
        return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'账号被锁定，登录失败！'})

    auth.login(request, user)
    if remember_me:
        remember_user(request, user)

    return simplejson.dumps({'ret_code': 0})

