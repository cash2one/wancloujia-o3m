# coding: utf-8
import re
import logging

from django import forms
from parsley.decorators import parsleyfy
from ajax_upload.widgets import AjaxClearableFileInput
from framework.widgets import Select2WidgetCN
from django_select2 import *

from models import *
from statistics.models import BrandModel

@parsleyfy
class AppForm(forms.ModelForm):
    package = forms.CharField(widget=forms.HiddenInput)
    app_icon = forms.CharField(label=u'应用图标', widget=AjaxClearableFileInput, required=False)

    class Meta:
        model = App
        fields = ('version', 'name', 'apk', 'category', 'online', 'popularize', 'desc', 'version_code')
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

class ModelChoices(AutoModelSelect2Field):
    queryset = BrandModel.objects
    search_fields = ['model__icontains']

class SubjectChoices(AutoModelSelect2Field):
    queryset = Subject.objects
    search_fields = ['name__icontains', ]

@parsleyfy
class SubjectMapModelForm(forms.ModelForm):
    model = ModelChoices(required=True, label=u'机型', widget=Select2WidgetCN(), to_field_name='model')
    subject = SubjectChoices(required=True, label=u'应用专题', widget=Select2WidgetCN())
    
    class Meta:
        model = SubjectMap

@parsleyfy
class SubjectMapMemSizeForm(forms.ModelForm):
    mem_size = Select2ChoiceField(choices=SubjectMap.MEM_SIZE_CHOICES, label=u'存储空间', widget=Select2WidgetCN())
    subject2 = SubjectChoices(required=True, label=u'应用专题', widget=Select2WidgetCN())

    class Meta:
        model = SubjectMap
