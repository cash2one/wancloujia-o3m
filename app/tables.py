# coding: utf-8
import logging

import django_tables2 as tables
from models import App, Subject
from mgr.models import cast_staff


class AppTable(tables.Table): 
    size = tables.Column(verbose_name=u'应用大小')
    subjects = tables.Column(verbose_name=u'所属应用专题')
    create_date = tables.TemplateColumn(verbose_name=u'创建时间', 
                                        template_code='{{ record.create_date|date:"Y-m-d H:i"}}')
    ops_3 = tables.TemplateColumn(verbose_name=u'操作', template_name="app_ops.html")

    def render_size(self, record):
        if record.size() == 0:
            return u'－'
        elif record.size() < 1024 * 1024:
            return ('%.2f KB' % (record.size() / 1024.0))
        else:
            return ('%.2f MB' % (record.size() / 1024.0 / 1024.0))

    def render_category(self, record):
        categories = []
        category = record.category
        while category:
            categories.append(category)
            category = category.parent
        categories.reverse()
        return "-".join([str(c) for c in categories])

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
        return creator.realname if creator.realname else u'—'

    def render_updator(self, record):
        user = cast_staff(record.updator if record.updator else record.creator)
        return user.realname if user.realname else u'—'

    class Meta:
        model = Subject
        fields = ('name', 'online', 'creator', 'create_date', 'updator', 'update_date')
        orderable = False
        attrs = {'class': 'table table-hover table-bordered'}
        empty_text = u'暂无应用专题'
