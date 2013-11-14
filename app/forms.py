# encoding: utf-8
import re

from django import forms
from parsley.decorators import parsleyfy
from ajax_upload.widgets import AjaxClearableFileInput

from models import *

@parsleyfy
class AppForm(forms.ModelForm):

    class Meta:
        model = App
        fields = ('name', 'version', 'package', 'apk', 'icon', 'category', 'popularize', 'desc')
        widgets = {
            'name': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'version': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'icon': AjaxClearableFileInput,
            'package': forms.HiddenInput,
            'desc': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'apk': forms.HiddenInput
        }

