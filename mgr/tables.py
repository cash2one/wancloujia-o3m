# coding: utf-8
import logging
import django_tables2 as tables
from models import cast_staff, Staff, Company, Store

class StaffTable(tables.Table):
    groups = tables.Column(verbose_name=u"所属用户组", empty_values=())
    type = tables.TemplateColumn(verbose_name=u"账号类型", template_name='user_type.html')
    organization = tables.Column(verbose_name=u"用户所属机构", empty_values=())
    ops = tables.TemplateColumn(verbose_name=u"操作", template_name="user_ops.html")

    def render_organization(self, record):
        staff = record.cast()
        if not hasattr(staff, "organization"):
            return u'—'

        return staff.organization.name

    def render_groups(self, record):
        if record.is_superuser or record.is_staff:
            return u'—'

        groups = record.groups.all()
        if len(groups) == 0:
            return u'—'

        return ', '.join([g.name for g in groups])

    class Meta:
        model = Staff
        sortable = False
        attrs = {'class': 'table table-hover table-bordered'}
        fields = ('username', 'realname')
        empty_text = '当前没有用户信息'


class StoreTable(tables.Table):
    ops = tables.TemplateColumn(verbose_name=u'操作', template_name='store_ops.html')

    class Meta:
        model = Store
        attrs = {'class': 'table table-hover table-bordered stores'}
        fields = ('code', 'name', 'company')
        sortable = False
        page_field = 'sp'
        empty_text = u'暂无门店'

class CompanyTable(tables.Table):
    stores = tables.TemplateColumn(verbose_name=u'门店数量', template_name="store_count.html")
    ops = tables.TemplateColumn(verbose_name=u'操作', template_name='company_ops.html')

    class Meta:
        model = Company
        sortable = False
        attrs = {'class': 'table table-hover table-bordered companies'}
        fields = ('code', 'name')
        page_field = 'cp'
        empty_text = u'暂无公司'

