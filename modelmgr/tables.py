# coding: utf-8
import logging

from django.utils.safestring import mark_safe
import django_tables2 as tables

from models import Model

logger = logging.getLogger(__name__)


class ModelTable(tables.Table):
    ops_2 = tables.TemplateColumn(verbose_name=u"操作", 
                                    template_name="model_ops.html")

    class Meta:
        model = Model
        orderable = False
        attrs = {'class': 'table table-hover table-bordered'}
        fields = ('name', 'ua')
        empty_text = '暂无机型'

