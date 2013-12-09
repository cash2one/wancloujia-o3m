# coding: utf-8
import logging

from django.contrib.contenttypes.models import ContentType
import django_tables2 as tables

from interface.models import LogMeta
from mgr.models import Employee, Organization, Region, Company, Store
from app.models import App

logger = logging.getLogger(__name__)

def _get_emp(id):
    emps = Employee.objects.filter(pk=id)        
    return emps[0] if len(emps) > 0 else None

def _get_app(package):
    apps = App.objects.filter(package=package)        
    return apps[0] if len(apps) > 0 else None

class LogTable(tables.Table):
    region = tables.Column(verbose_name=u'大区', empty_values=())
    uid = tables.Column(verbose_name=u'员工', empty_values=())
    app = tables.Column(verbose_name=u'应用', empty_values=())
    company = tables.Column(verbose_name=u'公司', empty_values=())
    store = tables.Column(verbose_name=u'门店', empty_values=())
    popularize = tables.Column(verbose_name=u'是否推广', empty_values=())
    date = tables.TemplateColumn(verbose_name=u'日期', template_code='''{{ record.date|date:"Y-m-d"}}''')

    def render_popularize(self, record):
        app = _get_app(record.appPkg) 
        if not app:
            return u'－'
        return u'推广' if app.popularize else u'不推广'

    def render_region(self, record):
        emp = _get_emp(record.uid)
        if not emp:
            return u'－'
        return emp.get_region().name if emp else u'－'

    def render_company(self, record):
        emp = _get_emp(record.uid)
        if not emp:
            return u'－'
        company = emp.get_company()
        return company.name if company else u'－'

    def render_store(self, record):
        emp = _get_emp(record.uid)
        if not emp:
            return u'－'
        store = emp.get_store()
        return store.name if store else u'－'

    def render_uid(self, record):
        emp = _get_emp(record.uid)
        return emp.username if emp else u'－'

    def render_app(self, record):
        app = _get_app(record.appPkg)
        return app.name if app else u'－'
    
    class Meta:
        model = LogMeta
        orderable = False
        attrs = {'class': 'table table-hover table-bordered'}
        fields = ('date', 'uid', 'did', 'brand', 'model')
        sequence = ('region', 'company', 'store', 'uid', 'brand', 'model', 'did', 'app', 'popularize', 'date')
        empty_text = '暂无统计'

