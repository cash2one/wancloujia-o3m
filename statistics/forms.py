#coding:utf-8
from django import forms

from interface.models import LogMeta
from app.models import App

class DownloadFilterForm(forms.Form):
    appNameOrPkg = forms.CharField(label=u'应用名称', max_length=App.PACKAGE_LENGTH_LIMIT, required=False)
    downloadModule = forms.CharField(label=u'版块', required=False)

    from_date = forms.DateField(label=u'开始时间', required=False)
    to_date = forms.DateField(label=u'结束时间', required=False)

class AdFilterForm(forms.Form):

    from_date = forms.DateField(label=u'开始时间', required=False)
    to_date = forms.DateField(label=u'结束时间', required=False)



class LogMetaFilterForm(forms.Form):
    region = forms.DecimalField(label=u'大区', required=False, min_value=1)
    company = forms.DecimalField(label=u'公司', required=False, min_value=1)
    store = forms.DecimalField(label=u'门店', required=False, min_value=1)
    emp = forms.DecimalField(label=u'员工', required=False, min_value=1)

    app = forms.CharField(label=u'应用名称', max_length=App.PACKAGE_LENGTH_LIMIT, required=False)
    brand =forms.CharField(label=u'品牌', max_length=LogMeta.BRAND_LENGTH_LIMIT, required=False)
    from_date = forms.DateField(label=u'开始时间', required=False)
    to_date = forms.DateField(label=u'结束时间', required=False)


class InstalledCapacityFilterForm(forms.Form):
    region = forms.DecimalField(label=u'大区', required=False, min_value=1)
    company = forms.DecimalField(label=u'公司', required=False, min_value=1)
    store = forms.DecimalField(label=u'门店', required=False, min_value=1)
    emp = forms.DecimalField(label=u'员工', required=False, min_value=1)

    app = forms.CharField(label=u'应用名称', max_length=App.PACKAGE_LENGTH_LIMIT, required=False)
    popularize = forms.CharField(label=u'是否推广', max_length=10, required=False)

    from_date = forms.DateField(label=u'开始时间', required=False)
    to_date = forms.DateField(label=u'结束时间', required=False)


class DeviceStatForm(forms.Form):
    region = forms.DecimalField(label=u'大区', required=False, min_value=1)
    company = forms.DecimalField(label=u'公司', required=False, min_value=1)
    store = forms.DecimalField(label=u'门店', required=False, min_value=1)
    emp = forms.DecimalField(label=u'员工', required=False, min_value=1)

    brand =forms.CharField(label=u'品牌', max_length=LogMeta.BRAND_LENGTH_LIMIT, required=False)
    model =forms.CharField(label=u'机型', max_length=255, required=False)
    app = forms.CharField(label=u'应用名称', max_length=App.PACKAGE_LENGTH_LIMIT, required=False)

    from_date = forms.DateField(label=u'开始时间', required=False)
    to_date = forms.DateField(label=u'结束时间', required=False)


class OrganizationStatForm(forms.Form):
    region = forms.DecimalField(label=u'大区', required=False, min_value=1)
    company = forms.DecimalField(label=u'公司', required=False, min_value=1)
    store = forms.DecimalField(label=u'门店', required=False, min_value=1)
    emp = forms.DecimalField(label=u'员工', required=False, min_value=1)

    from_date = forms.DateField(label=u'开始时间', required=False)
    to_date = forms.DateField(label=u'结束时间', required=False)

