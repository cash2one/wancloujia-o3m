# coding: utf-8
import re
import logging

from django import forms
from parsley.decorators import parsleyfy
from ajax_upload.widgets import AjaxClearableFileInput

from models import *


@parsleyfy
class AppForm(forms.ModelForm):
    package = forms.CharField(widget=forms.HiddenInput)
    app_icon = forms.CharField(label=u'应用图标', widget=AjaxClearableFileInput, required=False)

    class Meta:
        model = App
        fields = ('version', 'name', 'apk', 'category', 'online', 'popularize', 'desc')
        widgets = {
            'online': forms.HiddenInput,
            'version': forms.TextInput(attrs={
                'readonly': 'readonly', 
                'class': 'form-control'
            }),
            'desc': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': u'最多可以输入50个字',
                'maxlength': 50,
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'readonly': 'readonly', 
                'class': 'form-control'
            }),
            'apk': forms.HiddenInput
        }


@parsleyfy
class SubjectForm(forms.ModelForm):
    name = forms.CharField(label=u'专题名称', max_length=20)
    desc = forms.CharField(label=u'专题描述', max_length=100, required=False, 
                            widget=forms.Textarea(attrs={
                                'rows': 4, 
                                'class': 'form-control'
                            }))

    class Meta:
        model = Subject
        exclude = ('name', )
        widgets = {'cover': AjaxClearableFileInput}

