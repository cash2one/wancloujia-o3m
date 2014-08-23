# coding: utf-8
import logging

import django_tables2 as tables

from models import App, Subject, AppGroup
from mgr.models import cast_staff


def bitsize(bits):
    if bits < 1024 * 1024:
        return ('%.2f KB' % (bits / 1024.0))
    else:
        return ('%.2f MB' % (bits / 1024.0 / 1024.0))


class AppTable(tables.Table): 
    size = tables.Column(verbose_name=u'应用大小')
    subjects = tables.Column(verbose_name=u'所属应用专题', empty_values=())
    create_date = tables.TemplateColumn(verbose_name=u'创建时间', 
                                        template_code='{{ record.create_date|date:"Y-m-d H:i"}}')
    ops = tables.TemplateColumn(verbose_name=u'操作', template_name="app_ops.html")

    def render_size(self, record):
        return u'－' if record.size() == 0 else bitsize(record.size())
        
    def render_subjects(self, record):
        grps = AppGroup.objects.filter(app=record)
        return ", ".join([item.subject.name for item in grps]) if len(grps) > 0 else u'—'

    class Meta:
        model = App
        fields = ('id', 'name', 'version', 'create_date')
        orderable = False
        attrs = {'class': 'table table-hover table-bordered'}
        empty_text = u'暂无应用'


class SubjectTable(tables.Table):
    ops = tables.TemplateColumn(verbose_name=u'操作', template_name="subject_ops.html")
    
    class Meta:
        model = Subject
        fields = ('name',)
        orderable = False
        attrs = {'class': 'table table-hover table-bordered'}
        empty_text = u'暂无应用专题'
