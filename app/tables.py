# coding: utf-8
import logging

import django_tables2 as tables

from models import App, Subject, AppGroup, SubjectMap
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
    ops_3 = tables.TemplateColumn(verbose_name=u'操作', template_name="app_ops.html")

    def render_size(self, record):
        return u'－' if record.size() == 0 else bitsize(record.size())
        
    def render_category(self, record):
        categories = []
        category = record.category
        while category:
            categories.append(category)
            category = category.parent
        categories.reverse()
        return "-".join([str(c) for c in categories])

    def render_subjects(self, record):
        grps = AppGroup.objects.filter(app=record)
        return ", ".join([item.subject.name for item in grps]) if len(grps) > 0 else u'—'

    def render_online(self, record):
        return u'已上线' if record.online else u'已下线'

    class Meta:
        model = App
        fields = ('name', 'version', 'category', 'online', 'create_date')
        orderable = False
        attrs = {'class': 'table table-hover table-bordered'}
        empty_text = u'暂无应用'


class SubjectTable(tables.Table):
    ops_3 = tables.TemplateColumn(verbose_name=u'操作', template_name="subject_ops.html")
    create_date = tables.TemplateColumn(verbose_name=u'创建时间', 
                                        template_code='{{ record.create_date|date:"Y-m-d H:i"}}')
    update_date = tables.TemplateColumn(verbose_name=u'上次修改时间', 
                                        template_code='{{ record.update_date|date:"Y-m-d H:i"}}')
    
    def render_online(self, record):
        return u"已上线" if record.online else u"已下线"

    def render_creator(self, record):
        creator = cast_staff(record.creator)
        return creator.realname if creator.realname else creator.username

    def render_updator(self, record):
        user = cast_staff(record.updator if record.updator else record.creator)
        return user.realname if user.realname else user.username 

    class Meta:
        model = Subject
        fields = ('name', 'online', 'creator', 'create_date', 'updator', 'update_date')
        orderable = False
        attrs = {'class': 'table table-hover table-bordered'}
        empty_text = u'暂无应用专题'

class SubjectMapTable(tables.Table):
    ops_2 = tables.TemplateColumn(verbose_name=u'操作', template_name="subject_map_ops.html")
    create_date = tables.TemplateColumn(verbose_name=u'创建时间',
                                        template_code='{{ record.create_date|date:"Y-m-d H:i"}}')
    update_date = tables.TemplateColumn(verbose_name=u'上次修改时间',
                                        template_code='{{ record.update_date|date:"Y-m-d H:i"}}')
    def render_creator(self, record):
        creator = cast_staff(record.creator)
        return creator.realname if creator.realname else creator.username

    def render_updator(self, record):
        user = cast_staff(record.updator if record.updator else record.creator)
        return user.realname if user.realname else user.username

    class Meta:
        model = SubjectMap
        fields = ('type', 'model', 'mem_size', 'subject', 'creator', 'create_date', 'updator', 'update_date')
        orderable = False
        attrs = {'class': 'table table-hover table-bordered'}
        empty_text = u'暂无应用专题适配'
