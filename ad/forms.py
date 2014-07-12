#coding:utf-8
import re
from django import forms
from django.contrib.contenttypes.models import ContentType

from ajax_upload.widgets import AjaxClearableFileInput
from parsley.decorators import parsleyfy
from models import AD


class ADForm(forms.ModelForm):
    class Meta:
        model = AD
        widgets = {
            'title': forms.TextInput(attrs={
                'readonly': 'readonly', 
                'class': 'form-control'
            }),
            'cover': AjaxClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'link': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }

