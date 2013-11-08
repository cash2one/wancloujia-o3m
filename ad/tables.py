# coding: utf-8
import logging
import django_tables2 as tables

from models import AD

class ADTable(tables.Table):
    cover = tables.TemplateColumn(verbose_name=u'广告图片', template_name="ad_cover.html")
    visible = tables.Column(verbose_name=u'广告状态', empty_values=())
    desc = tables.TemplateColumn(verbose_name=u'广告介绍', template_name="ad_desc.html")
    period = tables.TemplateColumn(verbose_name=u'有效时间段', 
                                   template_code='''
                                        {{ record.from_date|date:"Y-m-d H:i"}} 
                                        - {{ record.to_date|date:"Y-m-d H:i"}}
                                   ''')
    ops_2 = tables.TemplateColumn(verbose_name=u"操作", template_name="ad_ops.html")

    def render_visible(self, record):
        return u'显示' if record.visible else u'隐藏'

    class Meta:
        model = AD
        sortable = False
        attrs = {'class': 'table table-hover table-bordered'}
        fields = ('title', 'cover', 'desc', 'visible')
        empty_text = '暂无广告'

