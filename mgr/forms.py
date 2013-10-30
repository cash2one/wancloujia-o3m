# encoding: utf-8
from django import forms
from parsley.decorators import parsleyfy

@parsleyfy
class ModifyPasswordForm(forms.Form):
    origin = forms.CharField(label=u'旧密码', max_length=16, min_length=6,
                             widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label=u'新密码', help_text='6~16个字符，区分大小写', 
                               max_length=16, min_length = 6, 
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm = forms.CharField(label=u'确认密码', max_length=16, min_length=6,
                              widget=forms.PasswordInput(attrs={'class': 'form-control', 
                                                                'data-twice': 'password'}))

    def clean(self):
        data = super(ModifyPasswordForm, self).clean()
        if data["password"] != data["confirm"]:
            raise forms.ValidationError(u"两次输入的密码不相同")
        return data


