# coding: utf-8
import logging

import django_tables2 as tables
from models import *


class AppTable(tables.Table): 
    size = tables.Column(verbose_name=u'应用大小')
    subjects = tables.Column(verbose_name=u'所属应用专题')
    ops_2 = tables.TemplateColumn(verbose_name=u'操作', template_name="app_ops.html")

    def render_size(self, record):
        if record.size() == 0:
            return u'－'
        elif record.size() < 1000 * 1000:
            return ('%.2fKB' % record.size() / 1000.0)
        else:
            return ('%.2fMB' % record.size() / 1000.0 / 1000.0)

    def render_category(self, record):
        categories = []
        category = record.category
        while category:
            categories.append(category)
            category = category.parent
        categories.reverse()
        return "-".join(categories)

    def render_subjects(self, record):
        return ", ".join([item.subject for item in AppGroup.objects.filter(app=record)])

    def render_popularize(self, record):
        return u'推广' if record.popularize else u'不推广'

    def render_online(self, record):
        return u'已上线' if record.online else u'已下线'

    class Meta:
        model = App
        fields = ('name', 'version', 'category', 'popularize', 'online', 'create_date')
        orderable = False
        attrs = {'class': 'table table-hover table-bordered'}

