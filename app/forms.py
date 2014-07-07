# coding: utf-8
import re
import logging

from django import forms
from parsley.decorators import parsleyfy
from ajax_upload.widgets import AjaxClearableFileInput

from models import *


class AppForm(forms.ModelForm):
    size = forms.CharField(label=u'应用大小', max_length=50, widget=forms.HiddenInput)
    screen2 = forms.CharField(label=u'应用截图2', required=False, widget=AjaxClearableFileInput(attrs={'class': 'form-control'}))
    screen3 = forms.CharField(label=u'应用截图3', required=False, widget=AjaxClearableFileInput(attrs={'class': 'form-control'}))
    screen4 = forms.CharField(label=u'应用截图4', required=False, widget=AjaxClearableFileInput(attrs={'class': 'form-control'}))
    screen5 = forms.CharField(label=u'应用截图5', required=False, widget=AjaxClearableFileInput(attrs={'class': 'form-control'}))
    screen6 = forms.CharField(label=u'应用截图6', required=False, widget=AjaxClearableFileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = App
        widgets = {
            'app_icon': AjaxClearableFileInput(attrs={'class': 'form-control'}),
            'screen1': AjaxClearableFileInput(attrs={'class': 'form-control'}),
            'slogan': forms.TextInput(attrs={'class': 'form-control'}),
            'version': forms.TextInput(attrs={
                'readonly': 'readonly', 
                'class': 'form-control'
            }),
            'desc': forms.TextInput(attrs={'class': 'form-control'}),
            'package': forms.TextInput(attrs={
                'readonly': 'readonly', 
                'class': 'form-control'
            }),
            'longDesc': forms.Textarea(attrs={
                'rows': 3, 
                'maxlength': 50,
                'class': 'form-control'
            }),
            'version': forms.TextInput(attrs={
                'readonly': 'readonly', 
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'readonly': 'readonly', 
                'class': 'form-control'
            }),
            'apk': forms.HiddenInput,
            'version_code': forms.HiddenInput
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

