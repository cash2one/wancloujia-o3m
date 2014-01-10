#coding: utf-8
import django_tables2 as tables
from oplog.models import op_log

class OpLogTable(tables.Table):
    date = tables.TemplateColumn(verbose_name=u'时间', template_code='''
                                        {{ record.date|date:"Y-m-d H:i"}}
                                   ''')
    user = tables.Column(verbose_name=u'用户', empty_values=())
    op = tables.Column(verbose_name=u'操作', empty_values=())

    def render_user(self, record):
        return record.username

    def render_op(self, record):
        return record.content


    class Meta:
        model = op_log
        orderable = False
        attrs = {'class': 'table table-hover table-bordered'}
        fields = ('op',)
        sequence = ('date', 'user', 'op')
        page_field = 'p'
        empty_text = u'暂无任何操作记录'