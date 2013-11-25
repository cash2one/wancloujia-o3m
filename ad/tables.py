# coding: utf-8
import logging

from django.utils.safestring import mark_safe
import django_tables2 as tables

from models import AD

logger = logging.getLogger(__name__)

class AvailableColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        super(AvailableColumn, self).__init__(*args, **kwargs)
        self.available_text =  u'显示'
        self.unavailable_text = u'隐藏'

    def render(self, record):
        if not record.available():
            return self.unavailable_text

        if record.in_period():
            return self.available_text

        return mark_safe(u'''<p>显示</p>
                            <p class='warn'>！不在有效期内</p>''')


class ADTable(tables.Table):
    cover = tables.TemplateColumn(verbose_name=u'广告图片', template_name="ad_cover.html")
    visible = AvailableColumn(verbose_name=u'广告状态', empty_values=())
    desc = tables.TemplateColumn(verbose_name=u'广告介绍', template_name="ad_desc.html")
    period = tables.TemplateColumn(verbose_name=u'有效时间段', 
                                   template_code='''
                                        {{ record.from_date|date:"Y-m-d H:i"}} 
                                        - {{ record.to_date|date:"Y-m-d H:i"}}
                                   ''')
    ops_2 = tables.TemplateColumn(verbose_name=u"操作", template_name="ad_ops.html")

    class Meta:
        model = AD
        orderable = False
        attrs = {'class': 'table table-hover table-bordered'}
        fields = ('title', 'cover', 'desc', 'visible')
        empty_text = '暂无广告'

