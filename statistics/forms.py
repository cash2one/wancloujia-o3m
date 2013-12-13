#coding:utf-8
from django import forms

from interface.models import LogMeta
from app.models import App


class LogMetaFilterForm(forms.Form):
    region = forms.DecimalField(label=u'大区', required=False, min_value=1)
    company = forms.DecimalField(label=u'公司', required=False, min_value=1)
    store = forms.DecimalField(label=u'门店', required=False, min_value=1)
    emp = forms.DecimalField(label=u'员工', required=False, min_value=1)
    app = forms.CharField(label=u'应用名称', max_length=App.PACKAGE_LENGTH_LIMIT, required=False)
    brand =forms.CharField(label=u'品牌', max_length=LogMeta.BRAND_LENGTH_LIMIT, required=False)
    from_date = forms.DateField(label=u'开始时间', required=False)
    to_date = forms.DateField(label=u'结束时间', required=False)

