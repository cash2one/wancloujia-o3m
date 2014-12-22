# encoding: utf-8
import re

from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from parsley.decorators import parsleyfy

from models import *
from suning.permissions import *
from suning.user_constraits import PWD_MAX_LEN, PWD_MIN_LEN
from ajax_upload.widgets import AjaxClearableFileInput



@parsleyfy
class ModifyPasswordForm(forms.Form):
    origin = forms.CharField(label=u'旧密码', max_length=16, min_length=6,
                             widget=forms.PasswordInput(attrs={
                                 'class': 'form-control'
                             }))
    password = forms.CharField(label=u'新密码', help_text='6~16个字符，区分大小写', 
                               max_length=PWD_MAX_LEN, min_length=PWD_MIN_LEN, 
                               widget=forms.PasswordInput(attrs={
                                   'class': 'form-control'
                               }))
    confirm = forms.CharField(label=u'确认密码', max_length=PWD_MAX_LEN, min_length=PWD_MIN_LEN,
                              widget=forms.PasswordInput(attrs={
                                   'data-equal': 'password',
                                   'class': 'form-control'
                              }))

    def clean(self):
        data = super(ModifyPasswordForm, self).clean()
        if data["password"] != data["confirm"]:
            raise forms.ValidationError(u"两次输入的密码不相同")
        return data


@parsleyfy
class ResetPasswordForm(forms.Form):
    password = forms.CharField(label=u'新密码', help_text='6~16个字符，区分大小写', 
                               max_length=16, min_length = 6, 
                               widget=forms.PasswordInput())
    confirm = forms.CharField(label=u'确认密码', max_length=16, min_length=6,
                              widget=forms.PasswordInput(attrs={'parsley-equal': 'password'}))


class TextInput(forms.TextInput):
    def __init__(self, attrs=None):
        attrs = {} if attrs is None else attrs
        classname = attrs['class'] if hasattr(attrs, "class") else ''
        classes = classname.split(" ")
        if not 'form-control' in classes:
            classes.append('form-control')
        attrs['class'] = ' '.join(classes)
        forms.TextInput.__init__(self, attrs)


@parsleyfy
class EmployeeForm(forms.ModelForm):
    user_permissions = forms.MultipleChoiceField(label=u'授权权限', required=False, 
                                                 choices=get_available_permissions())
    email = forms.EmailField(label=u'邮箱', required=True, 
            widget=forms.TextInput(attrs={
                'class': 'form-control'
            }))

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if not re.match("^\d{11}$", phone):
            raise forms.ValidationError(u'请输入正确的手机号码')
        return phone

    class Meta:
        model = Employee
        widgets = {
            'introduce': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'realname': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'tel': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }
        fields = ('id', 'username', 'realname', 'organization', 
                    'phone', 'email', 'tel', 'introduce')


@parsleyfy
class AdminForm(forms.ModelForm):
    email = forms.EmailField(label=u'邮箱', required=True, 
            widget=forms.TextInput(attrs={
                'class': 'form-control'
            }))

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if not re.match("^\d{11}$", phone):
            raise forms.ValidationError(u'请输入正确的手机号码')
        return phone
    
    class Meta:
        model = Administrator
        widgets = {
            'introduce': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'realname': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'tel': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }
        fields = ('username', 'realname', 'phone', 'email', 'tel', 'introduce')


@parsleyfy
class RegionForm(forms.Form):
    name = forms.CharField(label=u'名称', max_length=Organization.NAME_LENGTH_LIMIT,
            widget=forms.TextInput(attrs={
                'class': 'form-control'
            })) 


@parsleyfy
class CompanyForm(forms.ModelForm):
    code = forms.CharField(label=u'编码', max_length=Organization.CODE_LENGTH_LIMIT, 
                            widget=forms.TextInput(attrs={"parsley-type": "digits", 'class': 'form-control'}))
    name = forms.CharField(label=u'名称', max_length=Organization.NAME_LENGTH_LIMIT, 
            widget=forms.TextInput(attrs={
                'class': 'form-control'
            }))

    class Meta:
        model = Company
        fields = ('region',)
    

@parsleyfy
class StoreForm(forms.ModelForm):
    code = forms.CharField(label=u'编码', max_length=Organization.CODE_LENGTH_LIMIT, 
                            widget=forms.TextInput(attrs={"parsley-type": "digits", 'class': 'form-control'}))
    name = forms.CharField(label=u'名称', max_length=Organization.NAME_LENGTH_LIMIT,
            widget=forms.TextInput(attrs={
                'class': 'form-control'
            }))
    
    class Meta:
        model = Store
        fields = ('company',)


@parsleyfy
class GroupForm(forms.ModelForm):
    permissions = forms.MultipleChoiceField(label=u'授权权限', choices=get_available_permissions())
    name = forms.CharField(label=u'用户组名', max_length=80, 
            widget=forms.TextInput(attrs={
                'class': 'form-control'
            }))

    class Meta:
        model = Group
        fields = ('permissions',)


class PreferenceForm(forms.ModelForm):
    logo = forms.ImageField(required=False, widget=AjaxClearableFileInput())
    favicon = forms.ImageField(required=False, widget=AjaxClearableFileInput())
    vendor_prefix = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    color = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control pick-a-color'
    }))
    navbar_color = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control pick-a-color'
    }))

    class Meta:
        model = Preference
