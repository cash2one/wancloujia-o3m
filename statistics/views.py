#coding: utf-8
import logging
import datetime
import math
import HTMLParser 

import xlwt
from django import forms
from django.utils import simplejson
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query import QuerySet
from django.db.models import Q, Sum, Count
from django.views.decorators.http import require_GET, require_POST
from django_tables2.config import RequestConfig
from django.http import HttpResponse, Http404

from suning import settings
from suning import permissions
from suning.settings import EMPTY_VALUE
from suning.utils import render_json, first_valid, get_model_by_pk
from suning.decorators import active_tab
from mgr.models import cast_staff, Region, Company, Store, Organization, Employee
from app.models import App
from interface.models import LogMeta, InstalledAppLogEntity, DeviceLogEntity
from forms import LogMetaFilterForm, InstalledCapacityFilterForm
from forms import OrganizationStatForm, DeviceStatForm
from ajax import filter_flow_logs, log_to_dict, device_record_to_dict
from ajax import filter_installed_capacity_logs, installed_capacity_to_dict
from ajax import stat_device, filter_org_logs, org_record_to_dict
from statistics.models import BrandModel

logger = logging.getLogger(__name__)


def query_companies(user, rid):
    if not rid:
        return Company.objects.none()

    region = get_model_by_pk(Region.objects, rid)
    if not region:
        return Company.objects.none()

    if user.is_staff or user.is_superuser:
        return region.children()
    elif user.has_perm("interface.view_organization_statistics"):
        if user.org() != region:
            return Company.objects.none()
        else:
            return region.children() 
    else:
        return Company.objects.none()


def query_stores(user, cid):
    if not cid:
        return Store.objects.none()

    company = get_model_by_pk(Company.objects, cid)
    if not company:
        return Store.objects.none()

    if user.is_staff or user.is_superuser:
        return company.children()
    elif user.has_perm("interface.view_organization_statistics"):
        if user.in_store() or \
            (user.in_company() and user.org() != company) or \
            (user.in_region() and user.org() != company.region):
            return Store.objects.none()
        return company.children()
    else:
        return Store.objects.none()

 
def query_regions(user):
    if user.is_staff or user.is_superuser:
        return Region.objects.all()
    elif user.has_perm("interface.view_organization_statistics"):
        return [user.organizations()[0]]
    else:
        return Region.objects.none()


@require_GET
def regions(request):
    user = request.user
    if not user.is_authenticated():
        regions = Region.objects.none()

    dict = {}
    for r in query_regions(cast_staff(user)):
        dict[str(r.pk)] = r.name
    return render_json(dict)


@require_GET
def companies(request):
    user = request.user
    if not user.is_authenticated():
        companies = Company.objects.none()

    dict = {}
    for c in query_companies(cast_staff(user), request.GET.get('r', None)):
        dict[str(c.pk)] = "%s%s" % (c.code, c.name)
    return render_json(dict)


@require_GET
def stores(request):
    user = request.user
    if not user.is_authenticated():
        stores = Store.objects.none()

    dict = {}
    for s in query_stores(cast_staff(user), request.GET.get('c', None)):
        dict[str(s.pk)] = "%s%s" % (s.code, s.name)
    return render_json(dict)


def query_employee(user, org):
    if not org:
        return Employee.objects.none()

    if user.is_superuser or user.is_staff or org.belong_to(user.org()):
        return Employee.objects.filter_by_organization(org)
    else: 
        return Employee.objects.none()

def emps_to_dict_arr(emps):
    return map(lambda e: {'id': e.pk, 'text': e.username}, emps)


@require_GET
def employee(request):
    if not request.user.is_authenticated():
        return render_json({'results': emps_to_dict_arr(Employee.objects.none())})

    user = cast_staff(request.user)
    if not user.is_superuser and not user.is_staff and \
        not user.has_perm("interface.view_organization_statistics"):
        logger.debug("user has no permission to view organization's statistics")
        emps = Employee.objects.filter(pk=user.pk)
        return render_json({'results': emps_to_dict_arr(emps)})

    sid = request.GET.get('store', None)
    cid = request.GET.get('company', None)
    rid = request.GET.get('region', None)
    org_id = first_valid(lambda i: i, [sid, cid, rid])
    if not org_id:
        emps = Employee.objects.all()
    else:
        org = get_model_by_pk(Organization.objects, org_id) 
        org = org.cast() if org else None
        if not org:
            emps = Employee.objects.none()
        else:
            logger.debug("%s: org: %s" % (__name__, str(org)))
            emps = query_employee(user, org)

    LENGTH = 10
    q = request.GET.get("q", "")
    p = int(request.GET.get("p", '1'))
    emps = Employee.query(emps, q)
    total = len(emps)
    emps = emps[(p-1) * LENGTH: p * LENGTH]
    results = map(lambda e: {'id': e.pk, 'text': e.username}, emps)
    return render_json({'results': results, 'more': total > p * LENGTH})


@require_GET
def apps(request):
    if not request.user.is_authenticated():
        return render_json({'more': False, 'results': []})

    q = request.GET.get('q', "")
    p = request.GET.get('p', "")
    page = int(p) if p else 0

    APPS_PER_PAGE = 10
    apps = App.objects.filter(name__contains=q)
    total = len(apps)
    apps = apps[(page-1)*APPS_PER_PAGE:page*APPS_PER_PAGE]
    results = map(lambda e: {'id': e.pk, 'text': e.name}, apps)

    return render_json({'more': total > page * APPS_PER_PAGE, 'results': results})


@require_GET
def models(request):
    LENGTH = 10
    b = request.GET.get('b', '')
    q = request.GET.get('q', '') 
    p = int(request.GET.get('p', '1'))

    logs = BrandModel.objects.all()
    logs = logs.filter(brand=b) if b else logs
    logs = logs.filter(model__contains=q)
    models = logs.values_list('model', flat=True).distinct()
    return render_json({
        'more': len(models) > p * LENGTH,
        'models': models[(p-1) * LENGTH : p * LENGTH]
    })


@require_GET
def brands(request):
    LENGTH = 10
    q = request.GET.get('q', '') 
    p = int(request.GET.get('p', '1'))
    brands = BrandModel.objects.filter(brand__contains=q).values_list('brand', flat=True)
    return render_json({
        'more': len(brands) > p * LENGTH,
        'brands': brands[(p-1) * LENGTH : p * LENGTH]
    })

        
def user_filter(user):
    empty_value = {'pk': '', 'code': '', 'name': '--------'}
    user_filter = { 
        'region': { 'disabled': False, 'value': empty_value },
        'company': { 'disabled': False, 'value': empty_value },
        'store': { 'disabled': False, 'value': empty_value },
        'emp': { 'disabled': False }
    }

    if not user.is_superuser and not user.is_staff:
        organizations = [empty_value, empty_value, empty_value]
        for i, org in enumerate(user.organizations()):
            organizations[i] = org

        user_filter["region"]["value"] = organizations[0] 
        user_filter["region"]["disabled"] = organizations[0] is not empty_value

        user_filter["company"]["value"] = organizations[1] 
        user_filter["company"]["disabled"] = organizations[1] is not empty_value

        user_filter["store"]["value"] = organizations[2]
        user_filter["store"]["disabled"] = organizations[2] is not empty_value
        user_filter["emp"]["value"] = user

        if not user.has_perm("interface.view_organization_statistics"):
            logger.debug("user has no permission to view organization's statistices")
            user_filter["region"]["disabled"] = True
            user_filter["company"]["disabled"] = True
            user_filter["store"]["disabled"] = True
            user_filter["emp"]["disabled"] = True
    return user_filter


@require_GET
@login_required
@active_tab("statistics", "flow")
def flow(request):
    return render(request, "flow.html", {
        'user_filter': user_filter(cast_staff(request.user)),
        'filter': LogMetaFilterForm()
    })


@require_GET
@login_required
def flow_excel(request):
    filter_form = LogMetaFilterForm(request.GET)
    if not filter_form.is_valid():
        logger.warn("form is invalid")
        logger.warn(filter_form.errors)
        raise Http404

    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet(u'流水统计')
    default_style = xlwt.Style.default_style
    #date_style = xlwt.easyxf(num_format_str='yyyy-mm-dd')
    titles = [u'大区', u'公司', u'门店', u'员工', u'品牌', u'机型', u'串号', 
               u'应用序号', u'应用名称', u'应用包名', u'是否推广', u'日期']
    for i, title in enumerate(titles):
        sheet.write(0, i, title, style=default_style)

    user = cast_staff(request.user)
    logs = filter_flow_logs(user, filter_form)
    h = HTMLParser.HTMLParser()
    for row, log in enumerate(logs):
        logger.debug(log)
        dict = log_to_dict(log) 

        if dict['app']['popularize'] is None:
            popularize = h.unescape(EMPTY_VALUE)
        else:
            popularize = u'是' if dict['app']['popularize'] else u'否'
        app = dict['app']

        rowdata = [
            dict['region'] or h.unescape(EMPTY_VALUE),
            dict['company'] or h.unescape(EMPTY_VALUE),
            dict['store'] or h.unescape(EMPTY_VALUE),
            dict['emp'] or h.unescape(EMPTY_VALUE),
            dict['brand'] or h.unescape(EMPTY_VALUE),
            dict['model'] or h.unescape(EMPTY_VALUE),
            dict['device'] or h.unescape(EMPTY_VALUE),
            int(app['id']),
            app['name'] or h.unescape(EMPTY_VALUE),
            app['package'],
            popularize,
            dict['date'] 
        ]
        for col, val in enumerate(rowdata):
            #style = date_style if isinstance(val, datetime.date) else default_style
            style = default_style
            sheet.write(row+1, col, val, style=style)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=flow_statistics.xls'
    book.save(response)
    return response


@require_GET
@login_required
@active_tab("statistics", "capacity")
def capacity(request):
    return render(request, "capacity.html", {
        'user_filter': user_filter(cast_staff(request.user)),
        'filter': InstalledCapacityFilterForm()
    })


@require_GET
@login_required
def capacity_excel(request):
    filter_form = InstalledCapacityFilterForm(request.GET)
    if not filter_form.is_valid():
        logger.warn("form is invalid")
        logger.warn(filter_form.errors)
        raise Http404

    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet(u'安装统计')
    default_style = xlwt.Style.default_style
    #date_style = xlwt.easyxf(num_format_str='yyyy-mm-dd')
    titles = [u'应用序号', u'应用名称', u'应用包名', u'是否推广', u'安装总量']
    for i, title in enumerate(titles):
        sheet.write(0, i, title, style=default_style)

    user = cast_staff(request.user)
    logs = filter_installed_capacity_logs(user, filter_form)
    h = HTMLParser.HTMLParser()
    for row, log in enumerate(logs):
        logger.debug(log)
        dict = installed_capacity_to_dict(log) 
        rowdata = [
            dict['app']['id'],
            dict['app']['name'],
            dict['app']['package'],
            u'是' if dict['app']['popularize'] else u'否',
            dict['count']
        ]
        for col, val in enumerate(rowdata):
            #style = date_style if isinstance(val, datetime.date) else default_style
            style = default_style
            sheet.write(row+1, col, val, style=style)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=capacity_statistics.xls'
    book.save(response)
    return response


@require_GET
@login_required
@active_tab("statistics", "device")
def device(request):        
    return render(request, "device.html", {
        'user_filter': user_filter(cast_staff(request.user)),
        'filter': DeviceStatForm()
    })

@require_GET
@login_required
@active_tab("statistics", "device")
def device_excel(request):        
    filter_form = DeviceStatForm(request.GET)
    if not filter_form.is_valid():
        logger.warn("form is invalid")
        logger.warn(filter_form.errors)
        raise Http404

    user = cast_staff(request.user)

    def _device_record_to_array(record):
        return [
            record['model'],
            record['total_device_count'],
            record['total_popularize_count'],
            record['total_app_count']
        ]
    sheet_summary = {
        'name': u'机型统计_汇总',
        'titles': [u'机型', u'机器数', u'推广数', u'安装总数'],
        'records': stat_device(user, filter_form),
        'record_to_array': _device_record_to_array
    }

    def _device_detail_record_to_array(log):
        h = HTMLParser.HTMLParser()
        dict = device_record_to_dict(log)
        return [
            dict['emp'] or h.unescape(EMPTY_VALUE),
            dict['brand'],
            dict['model'],
            dict['device'],
            dict['total_popularize_count'],
            dict['total_app_count'],
        ]
    sheet_detail = {
        'name': u'机型统计_明细',
        'titles': [u'员工', u'品牌', u'机型', u'串号', u'推广数', u'安装总数'],
        'record_to_array': _device_detail_record_to_array,
        'records': stat_device(user, filter_form, True)
    }
    sheets = [sheet_summary, sheet_detail]
    return render_excel('device_summary_statistics.xls', sheets)
    

def render_excel(filename, sheets):
    book = xlwt.Workbook(encoding='utf8')
    default_style = xlwt.Style.default_style
    #date_style = xlwt.easyxf(num_format_str='yyyy-mm-dd')
    for sheet_info in sheets:
        sheet = book.add_sheet(sheet_info['name'])
        for i, title in enumerate(sheet_info['titles']):
            sheet.write(0, i, title, style=default_style)

        for row, record in enumerate(sheet_info['records']):
            array = sheet_info['record_to_array'](record)
            logger.debug(array)
            for col, val in enumerate(array):
                #style = date_style if isinstance(val, datetime.date) else default_style
                style = default_style
                sheet.write(row+1, col, val, style=style)

    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    book.save(response)
    return response

@require_GET
@login_required
@active_tab("statistics", "organization")
def organization(request):        
    return render(request, "organization_stat.html", {
        'user_filter': user_filter(cast_staff(request.user)),
        'filter': OrganizationStatForm()
    })

@require_GET
@login_required
def organization_excel(request, mode):        
    filter_form = OrganizationStatForm(request.GET)
    if not filter_form.is_valid():
        logger.warn("form is invalid")
        logger.warn(filter_form.errors)
        raise Http404

    user = cast_staff(request.user)
    logger.debug('mode: ' + mode)
    logs = filter_org_logs(filter_form, mode)
    key = mode if mode != 'emp' and mode != 'emp_only' else 'uid'
    records = logs.values(key).annotate(total_device_count=Count('did', distinct=True),
                                       total_popularize_count=Sum('popularizeAppCount'),
                                       total_app_count=Sum('appCount'))


    def _record_to_array(record):
        logger.debug(record)
        h = HTMLParser.HTMLParser()
        dict = org_record_to_dict(record, mode)
        array = []
        if mode == 'region':
            array.append(dict['region'] or h.unescape(EMPTY_VALUE))
        elif mode == 'store' or mode == 'company':
            array.append(dict[mode]['code'] or h.unescape(EMPTY_VALUE))
            array.append(dict[mode]['name'] or h.unescape(EMPTY_VALUE))
        else:
            array.append(dict['emp']['username'] or h.unescape(EMPTY_VALUE));
            array.append(dict['emp']['realname'] or h.unescape(EMPTY_VALUE));
        array.append(dict['total_device_count']) 
        array.append(dict['total_popularize_count']) 
        array.append(dict['total_app_count']) 
        return array

    titles = []
    if mode == 'region':
        titles = [u'分区', u'机器台数', u'推广数', u'安装总数']
    elif mode == 'company':
        titles = [u'编码', u'公司名称', u'机器台数', u'推广数', u'安装总数']
    elif mode == 'store':
        titles = [u'编码', u'门店名称', u'机器台数', u'推广数', u'安装总数']
    else:
        titles = [u'员工工号', u'员工姓名', u'机器台数', u'推广数', u'安装总数']

    sheet = {
        'name': u'组织统计',
        'titles': titles,
        'records': records,
        'record_to_array': _record_to_array
    }

    return render_excel('organization_statisitcs.xls', [sheet])

