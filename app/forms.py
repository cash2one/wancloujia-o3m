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
        fields = ('version', 'name', 'apk', 'category', 'popularize', 'desc')
        widgets = {
            'version': forms.TextInput(attrs={
                'readonly': 'readonly', 
                'class': 'form-control'
            }),
            'desc': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'readonly': 'readonly', 
                'class': 'form-control'
            }),
            'apk': forms.HiddenInput
        }

