#coding:utf-8
import re
from django import forms
from django.contrib.contenttypes.models import ContentType

from ajax_upload.widgets import AjaxClearableFileInput
from parsley.decorators import parsleyfy
from models import AD


@parsleyfy
class ADForm(forms.ModelForm):
    title = forms.CharField(label=u'广告标题', max_length=50, required=True)

    class Meta:
        model = AD
        excludes = ('title',)
        widgets = {
            'to_date': forms.TextInput(attrs={
                'readonly': '',
                'data-date-language': 'zh-CN',
                'data-date-format': 'yyyy-mm-dd hh:ii',
                'data-provide': 'datetimepicker'
            }),
            'from_date': forms.TextInput(attrs={
                'readonly': '',
                'data-date-language': 'zh-CN',
                'data-date-format': 'yyyy-mm-dd hh:ii',
                'data-provide': 'datetimepicker'
            }), 
            'desc': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control'
            }),
            'cover': AjaxClearableFileInput
        }

