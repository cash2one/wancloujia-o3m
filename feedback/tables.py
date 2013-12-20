#coding: utf-8
import django_tables2 as tables
from feedback.models import Feedback, HandledFeedback

class FeedbackTable(tables.Table):
    eid = tables.Column(verbose_name=u'序号', empty_values=())
    brand = tables.Column(verbose_name=u'品牌', empty_values=())
    model = tables.Column(verbose_name=u'型号', empty_values=())
    content = tables.Column(verbose_name=u'反馈内容')
    name = tables.Column(verbose_name=u'反馈人', empty_values=())
    tel = tables.Column(verbose_name=u'联系方式', empty_values=())
    date = tables.TemplateColumn(verbose_name=u'反馈时间', template_code='''
                                        {{ record.date|date:"Y-m-d H:i"}}
                                   ''')
    ops = tables.TemplateColumn(verbose_name=u"操作", template_name="inbox_ops.html")

    def render_name(self, record):
        return record.user.realname

    def render_eid(self, record):
        return record.pk

    def render_tel(self, record):
        return record.user.phone

    class Meta:
        model = Feedback
        orderable = False
        attrs = {'class': 'table table-hover table-bordered'}
        fields = ('content',)
        sequence = ('eid', 'brand', 'model', 'content', 'name', 'tel', 'date')
        page_field = 'p'
        empty_text = u'暂无任何反馈'


class HandledFeedbackTable(tables.Table):
    eid = tables.Column(verbose_name=u'序号', empty_values=())
    brand = tables.Column(verbose_name=u'品牌', empty_values=())
    model = tables.Column(verbose_name=u'型号', empty_values=())
    content = tables.Column(verbose_name=u'反馈内容')
    name = tables.Column(verbose_name=u'反馈人', empty_values=())
    tel = tables.Column(verbose_name=u'联系方式', empty_values=())
    date = tables.TemplateColumn(verbose_name=u'反馈时间', template_code='''
                                        {{ record.date|date:"Y-m-d H:i"}}
                                   ''')
    ops = tables.TemplateColumn(verbose_name=u"操作", template_name="handled_ops.html")

    def render_name(self, record):
        return record.user.realname

    def render_eid(self, record):
        return record.pk

    def render_tel(self, record):
        return record.user.phone

    class Meta:
        model = HandledFeedback
        orderable = False
        attrs = {'class': 'table table-hover table-bordered'}
        fields = ('content',)
        sequence = ('eid', 'brand', 'model', 'content', 'name', 'tel', 'date')
        page_field = 'p'
        empty_text = u'暂无任何已处理的反馈'