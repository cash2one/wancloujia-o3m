import re
from django import forms
from django.contrib.contenttypes.models import ContentType

from parsley.decorators import parsleyfy
from models import AD


@parsleyfy
class ADForm(forms.ModelForm):
    class Meta:
        model = AD
        widgets = {
            'online_date': forms.TextInput(attrs={
                'readonly': '',
                'data-date-language': 'zh-CN',
                'data-date-format': 'yyyy/mm/dd hh:ii',
                'data-provide': 'datetimepicker'
            }),
            'offline_date': forms.TextInput(attrs={
                'readonly': '',
                'data-date-language': 'zh-CN',
                'data-date-format': 'yyyy/mm/dd hh:ii',
                'data-provide': 'datetimepicker'
            })

        }

