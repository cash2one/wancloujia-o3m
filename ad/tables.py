# coding: utf-8
import logging
import django_tables2 as tables
from models import AD

class ADTable(tables.Table):
    ops = tables.TemplateColumn(verbose_name=u"操作", template_name="ad_ops.html")

    class Meta:
        model = AD
        sortable = False
        attrs = {'class': 'table table-hover table-bordered'}
        fields = ('title', 'cover', 'visible', 'online_date', 'offline_date')
        empty_text = '暂无广告'



