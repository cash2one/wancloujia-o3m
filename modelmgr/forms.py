#coding:utf-8
import re
from django import forms
from django.contrib.contenttypes.models import ContentType

from ajax_upload.widgets import AjaxClearableFileInput
from parsley.decorators import parsleyfy
from models import Model


@parsleyfy
class ModelForm(forms.Form):
    ua = forms.CharField(label=u'机型代码', max_length=100, required=True)
    name = forms.CharField(label=u'机型名称', max_length=100, required=True)