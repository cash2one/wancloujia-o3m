# coding: utf-8
from django import forms

from og.user_constraits import PWD_MAX_LEN, PWD_MIN_LEN, USERNAME_MAX_LEN

class LoginForm(forms.Form):
    username = forms.CharField(label=u'用户名', max_length=USERNAME_MAX_LEN)
    password = forms.CharField(label=u'密码', min_length=PWD_MIN_LEN, max_length=PWD_MAX_LEN)
    remember_me = forms.BooleanField()
