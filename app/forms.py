# coding: utf-8
import re
import logging

from django import forms
from parsley.decorators import parsleyfy
from ajax_upload.widgets import AjaxClearableFileInput
from taggit.forms import TagField
from taggit.models import Tag

from models import *



class AppForm(forms.ModelForm):
    size = forms.CharField(label=u'应用大小', max_length=50, widget=forms.HiddenInput)
    screen2 = forms.CharField(label=u'应用截图2', required=False, widget=AjaxClearableFileInput(attrs={'class': 'form-control'}))
    screen3 = forms.CharField(label=u'应用截图3', required=False, widget=AjaxClearableFileInput(attrs={'class': 'form-control'}))
    screen4 = forms.CharField(label=u'应用截图4', required=False, widget=AjaxClearableFileInput(attrs={'class': 'form-control'}))
    screen5 = forms.CharField(label=u'应用截图5', required=False, widget=AjaxClearableFileInput(attrs={'class': 'form-control'}))
    screen6 = forms.CharField(label=u'应用截图6', required=False, widget=AjaxClearableFileInput(attrs={'class': 'form-control'}))
    tags = forms.CharField(label=u'标签', widget=forms.HiddenInput)

    class Meta:
        model = App
        exclude = ["download_num","like_num","comment_num"]
        widgets = {
            'app_icon': AjaxClearableFileInput(attrs={'class': 'form-control'}),
            'screen1': AjaxClearableFileInput(attrs={'class': 'form-control'}),
            'slogan': forms.TextInput(attrs={'class': 'form-control'}),
            'version': forms.TextInput(attrs={
                'readonly': 'readonly', 
                'class': 'form-control'
            }),
            'sdk_version': forms.TextInput(attrs={
                'readonly': 'readonly', 
                'class': 'form-control'
            }),
            'desc': forms.TextInput(attrs={'class': 'form-control'}),
            'package': forms.TextInput(attrs={
                'readonly': 'readonly', 
                'class': 'form-control'
            }),
            'longDesc': forms.Textarea(attrs={
                'rows': 8, 
                'maxlength': 1000,
                'class': 'form-control'
            }),
            'permissions': forms.Textarea(attrs={
                'readonly': 'readonly', 
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
            'version_code': forms.HiddenInput,
        }


@parsleyfy
class SubjectForm(forms.ModelForm):
    name = forms.CharField(label=u'专题名称', max_length=20,  widget=forms.TextInput(attrs={
                    'class': 'form-control' 
                    #'readonly': 'readonly'
            }))

    class Meta:
        model = Subject
        #exclude = ('name', )

