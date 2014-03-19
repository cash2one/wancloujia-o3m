# coding: utf-8
import logging
from datetime import datetime

from django.utils import simplejson
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form

from interface.models import LogMeta, InstalledAppLogEntity, DeviceLogEntity
from interface.models import UserDeviceLogEntity
from app.models import App, Subject
from mgr.models import Staff, Employee, Organization, cast_staff, Region, Company, Store
from statistics.forms import LogMetaFilterForm, InstalledCapacityFilterForm
from statistics.forms import DeviceStatForm, OrganizationStatForm
from suning import utils
from suning.decorators import *
from models import query_model_name
import re

logger = logging.getLogger(__name__)
_invalid_data_msg = u'数据出错，请检查'
_invalid_data_json = simplejson.dumps({'ret_code': 1000, 'ret_msg': _invalid_data_msg})
_ok_json = simplejson.dumps({'ret_code': 0})

class UserFilter:
    def __init__(self, logs, user_id):
        self.logs = logs
        self.user_id = user_id

    def filter(self):
        return self.logs if not self.user_id else self.logs.filter(uid=self.user_id)

class AdminFilter:
    def __init__(self, logs, region_id, company_id, store_id, emp_id):
        self.logs = logs
        self.org_id = utils.first_valid(lambda e: e, [store_id, company_id, region_id])
        self.emp_id = emp_id = emp_id
        logger.debug("%s emp_id: %s, org_id: %s:" %(__name__, str(self.emp_id), str(self.org_id)))

    def filter(self):
        if self.emp_id:
            return self.logs.filter(uid=self.emp_id)

        if not self.org_id:
            return self.logs

        org = utils.get_model_by_pk(Organization.objects, self.org_id)
        if not org:
            return self.logs

        return self.logs.filter_by_organization(org.cast())


class UserPermittedFilter(AdminFilter):
    def __init__(self, user, logs, region_id, company_id, store_id, emp_id):
        AdminFilter.__init__(self, logs, region_id, company_id, store_id, emp_id)
        self.user = user

    def filter(self):
        user_org = self.user.org()

        if self.emp_id:
            emp = utils.get_model_by_pk(Employee.objects, self.emp_id) 
            if emp and emp.belong_to(user_org):
                return self.logs.filter(uid=self.emp_id)
            else: 
                return self.logs.none()

        if self.org_id:
            org = utils.get_model_by_pk(Organization.objects, self.org_id) 
            org = org.cast() if org else None
            if org and org.belong_to(user_org):
                return self.logs.filter_by_organization(org)
            else:
                return self.logs.none()

        return self.logs.filter_by_organization(user_org)


class UserUnpermittedFilter:

    def __init__(self, logs, user_id):
        self.logs = logs
        self.user_id = user_id

    def filter(self):
        return self.logs.filter(uid=self.user_id)


class PeriodFilter:
    def __init__(self, logs, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date
        self.logs = logs

    def filter(self):
        logs = self.logs
        if self.from_date:
            logs = logs.filter(date__gte=self.from_date)

        if self.to_date:
            logs = logs.filter(date__lte=self.to_date)

        return logs

class DeviceFilter:
    def __init__(self, logs, device):
        self.logs = logs
        self.device = device
    
    def filter(self):
        logs = self.logs
        return logs if not self.device else logs.filter(did=self.device)

class ModelFilter:
    def __init__(self, logs, model):
        self.logs = logs
        self.model = model
    
    def filter(self):
        logs = self.logs
        return logs if not self.model else logs.filter(model=self.model)

class BrandFilter:
    def __init__(self, logs, brand):
        self.logs = logs
        self.brand = brand

    def filter(self):
        logs = self.logs
        return logs if not self.brand else logs.filter(brand=self.brand)


class AppFilter:
    def __init__(self, logs, app):
        self.app = app
        self.logs = logs

    def filter(self):
        if not self.app:
            return self.logs

        apps = App.objects.filter(pk=self.app)
        if len(apps) == 0:
            return self.logs.none()
                
        app = apps[0]
        return self.logs.filter(appPkg=app.package)

class SubjectFilter:
    def __init__(self, logs, subject_id):
        self.subject_id = subject_id
        self.logs = logs

    def filter(self):
        return self.logs if not self.subject_id else self.logs.filter(subject=self.subject_id)

def log_to_dict(log):
    dict = {
		'date': str(log.date),
        'model': query_model_name(log.model),
        'device': log.did,
        'client_version': log.client_version,
        'installed': log.installed,
    }
    pici = ''

    subjects = Subject.objects.filter(pk=log.subject)
    subject = subjects[0] if len(subjects) != 0 else None
    dict["subject"] = {
        'id': subject.pk if subject else None, 
        'name': subject.name if subject else None,
    }
    try:
        m = re.match(r'^[^\#]*\#[^\#]*\#(?P<pici>.*)', dict['subject']['name']).groupdict()
        pici = m['pici']
    except:
        pass
    user = utils.get_model_by_pk(Staff.objects, log.uid)
    if user:
        dict["user"] = user.username
    else:
        dict["user"] = None
    dict['pici'] = pici
    return dict;

    
def filter_flow_logs(user, form):
    logs = LogMeta.objects.all().order_by('-date')
    from_date = form.cleaned_data["from_date"]
    to_date = form.cleaned_data["to_date"]
    logs = PeriodFilter(logs, from_date, to_date).filter() 
    logger.debug("logs filtered by period: %d" % len(logs))

    if user.is_superuser or user.is_staff or user.has_perm('interface.view_all_data'):
        user_id = form.cleaned_data["user"]
        logs = UserFilter(logs, user_id).filter()
        logger.debug("logs filtered by user info: %d" % len(logs))
    else:
        user_id = user.pk
        logs = UserFilter(logs, user_id).filter()
        logger.debug("logs filtered by user info: %d" % len(logs))

    logs = SubjectFilter(logs, form.cleaned_data["subject"]).filter()
    logger.debug("logs filtered by subject: %d" % len(logs))

    logs = ModelFilter(logs, form.cleaned_data["model"]).filter()
    logger.debug("logs filtered by model: %d" % len(logs))

    logs = DeviceFilter(logs, form.cleaned_data["device"]).filter()
    logger.debug("logs filtered by device: %d" % len(logs))

    installed = form.cleaned_data["installed"]
    if installed:
        logs = logs.filter(installed=(installed=='True'))

    return logs

@dajaxice_register(method='POST')
@check_login
def get_flow_logs(request, form, offset, length):
    user = cast_staff(request.user)
    form = deserialize_form(form)

    filter_form = LogMetaFilterForm(form)
    if not filter_form.is_valid():
        logger.warn("form is invalid")
        logger.warn(filter_form.errors)
        return _invalid_data_json

    logs = filter_flow_logs(user, filter_form)
    total = logs.count()
    devices = len(set([i.did for i in logs if i.did]))
    logs = logs[offset: offset + length]
    dict_list = []
    for log in logs:
        dict_list.append(log_to_dict(log))

    return simplejson.dumps({
        'ret_code': 0,
        'logs': dict_list,
        'total': total,
        'devices': devices
    })           

def filter_installed_capacity_logs(user, form):
    region_id = form.cleaned_data["region"]
    company_id = form.cleaned_data["company"]
    store_id = form.cleaned_data["store"]
    emp_id = form.cleaned_data["emp"]
    from_date = form.cleaned_data["from_date"]
    to_date = form.cleaned_data["to_date"]
    logs = InstalledAppLogEntity.objects.all()
    logs = PeriodFilter(logs, from_date, to_date).filter()
    if emp_id:
        logs = InstalledAppLogEntity.objects.filter(uid=emp_id)
    elif store_id:
        logs = InstalledAppLogEntity.objects.filter(store=store_id)
    elif company_id:
        logs = InstalledAppLogEntity.objects.filter(company=company_id)
    elif region_id:
        logs = InstalledAppLogEntity.objects.filter(region=region_id)
    else:
        pass#logs = InstalledAppLogEntity.objects.all()

    logger.debug("logs filtered by user info: %d" % len(logs))

    logs = AppFilter(logs, form.cleaned_data["app"]).filter()
    logger.debug("logs filtered by app: %d" % len(logs))

    
    logger.debug("logs filtered by period: %d" % len(logs))

    popularize = form.cleaned_data['popularize']
    if popularize:
        logs = logs.filter(popularize=(popularize=='True'))

    results = logs.values('appID', 'appName', 'appPkg', 'uid', 'region', 'company', 'store').annotate(count=Sum('installedTimes'))
    return results


def installed_capacity_to_dict(capacity):
    logger.debug(capacity) 
    dict = {}
    apps = App.objects.filter(package=capacity['appPkg'])
    app = apps[0] if len(apps) != 0 else None
    dict["app"] = {
        'id': capacity['appID'],
        'package': capacity['appPkg'],
        'name': capacity['appName'],
    }
    emp = utils.get_model_by_pk(Employee.objects, capacity['uid'])
    organizations = [None, None, None]
    if emp:
        dict["empid"] = emp.username
        dict["emp"] = emp.realname
        for i, item in enumerate(emp.organizations()):
            organizations[i] = item.name
    else:
        dict["emp"] = None
    dict["region"], dict["company"], dict["store"] = organizations
    dict["count"] = capacity['count']
    return dict;
    

@dajaxice_register(method='POST')
@check_login
def get_installed_capacity(request, form, offset, length):
    user = cast_staff(request.user)
    form = deserialize_form(form)

    filter_form = InstalledCapacityFilterForm(form)
    if not filter_form.is_valid():
        logger.warn("form is invalid")
        logger.warn(filter_form.errors)
        return _invalid_data_json

    results = filter_installed_capacity_logs(user, filter_form)
    total = len(results)
    devices = sum([i['count'] for i in results])
    results = results[offset: offset + length]
    dict_list = []
    for result in results:
        dict_list.append(installed_capacity_to_dict(result))

    return simplejson.dumps({
        'ret_code': 0,
        'logs': dict_list,
        'total': total,
        'devices': devices
    })


class MgrInfoFilter():
    def __init__(self, logs, region, company, store, emp):
        self.logs = logs
        self.region = region
        self.company = company
        self.store = store
        self.emp = emp

    def filter(self):
        logs = self.logs
        if self.emp:
            return logs.filter(uid=self.emp)
        elif self.store:
            return logs.filter(store=self.store)
        elif self.company:
            return logs.filter(company=self.company)
        elif self.region:
            return logs.filter(region=self.region)
        else:
            return logs


def _filter_device_statistics(user, form):
    region_id = form.cleaned_data["region"]
    company_id = form.cleaned_data["company"]
    store_id = form.cleaned_data["store"]
    emp_id = form.cleaned_data["emp"]
    from_date = form.cleaned_data["from_date"]
    to_date = form.cleaned_data["to_date"]
    logs = PeriodFilter(DeviceLogEntity.objects.all(), from_date, to_date).filter()
    logs = MgrInfoFilter(logs, form.cleaned_data["region"],
                         form.cleaned_data["company"], form.cleaned_data["store"], 
                         form.cleaned_data["emp"]).filter()
    logger.debug("logs filtered by mgr info: %d" % len(logs))

    logs = AppFilter(logs, form.cleaned_data["app"]).filter()
    logger.debug("logs filtered by app: %d" % len(logs))

    brand = form.cleaned_data["brand"]
    if brand:
        logs = logs.filter(brand=brand)
    model = form.cleaned_data["model"]
    if model:
        logs = logs.filter(model=model)
        

    
    logger.debug("logs filtered by period: %d" % len(logs))
    return logs


def stat_device(user, form, detail=False):
    logs = _filter_device_statistics(user, form) 
    if detail:
        logs = logs.values('uid', 'brand', 'model', 'did') 
        return logs.annotate(total_popularize_count=Sum('popularizeAppCount'), 
                             total_app_count=Sum('appCount'))
    else:
        logs =logs.values('model')
        return logs.annotate(total_device_count=Count('did', distinct=True), 
                             total_popularize_count=Sum('popularizeAppCount'), 
                             total_app_count=Sum('appCount'))


def count_device(user, form):
    logs = _filter_device_statistics(user, form) 
    return logs.aggregate(total=Sum('appCount'))['total']


@dajaxice_register(method='POST')
@check_login
def get_device_stat(request, form, offset, length):
    user = cast_staff(request.user)
    form = deserialize_form(form)

    filter_form = DeviceStatForm(form)
    if not filter_form.is_valid():
        logger.warn("form is invalid")
        logger.warn(filter_form.errors)
        return _invalid_data_json

    results = stat_device(user, filter_form)
    total = len(results)
    lst = [i['total_device_count'] for i in results if i['total_device_count']]
    devices = sum(lst)
    capacity = count_device(user, filter_form)
    results = results[offset: offset + length]
    dict_list = []
    for result in results:
        dict_list.append(result)
    return simplejson.dumps({
        'ret_code': 0,
        'logs': dict_list,
        'total': total,
        'capacity': capacity,
        'devices': devices
    })


def device_record_to_dict(record):
    emp = utils.get_model_by_pk(Employee.objects, record['uid'])
    username = emp.username if emp else None
    return {
        'brand': record['brand'],
        'model': record['model'],
        'device': record['did'],
        'total_popularize_count': record['total_popularize_count'],
        'total_app_count': record['total_app_count'],
        'emp': username
    }


@dajaxice_register(method='POST')
@check_login
def get_device_stat_detail(request, form, offset, length):
    user = cast_staff(request.user)
    form = deserialize_form(form)

    filter_form = DeviceStatForm(form)
    if not filter_form.is_valid():
        logger.warn("form is invalid")
        logger.warn(filter_form.errors)
        return _invalid_data_json

    results = stat_device(user, filter_form, True)
    total = len(results)
    capacity = count_device(user, filter_form)
    results = results[offset: offset + length]
    lst = [i['did'] for i in results if i['did']]
    devices = len(set(lst))
    logger.debug(results)
    dict_list = []
    for result in results:
        dict_list.append(device_record_to_dict(result))

    return simplejson.dumps({
        'ret_code': 0,
        'logs': dict_list,
        'total': total,
        'capacity': capacity,
        'devices': devices
    })


def filter_org_logs(form, mode):
    logs = DeviceLogEntity.objects.all()
    from_date = form.cleaned_data["from_date"]
    to_date = form.cleaned_data["to_date"]
    logs = PeriodFilter(logs, from_date, to_date).filter()
    if mode == 'region':
        pass#logs = DeviceLogEntity.objects.all()
    elif mode == 'company':
        region = form.cleaned_data['region']
        logs = logs.filter(region=region)
    elif mode == 'store':
        company = form.cleaned_data['company']
        logs = logs.filter(company=company)
    elif mode == 'emp':
        store = form.cleaned_data['store']
        logs = logs.filter(store=store)
    else:
        uid = form.cleaned_data['emp']
        logs = logs.filter(uid=uid)
    #if mode == 'did':
    #    results = logs.values('uid', 'did').annotate(total_popularize_count=Sum('popularizeAppCount'), total_app_count=Sum('appCount'))
    logger.debug("logs filtered by period: %d" % len(logs))
    return logs


_LEVELS = ['region', 'company', 'store', 'emp','did'] 
def available_levels(mode, level):
    offset = _LEVELS.index(mode)
    to = _LEVELS.index(level)
    return _LEVELS[offset:to+1]


def titles_for_org_stat(mode, level):
    levels = available_levels(mode, level)
    titles = []
    for level in levels:
        if level == 'region':
            titles.append(u'大区')
        elif level == 'company':
            titles.append(u'公司编码')
            titles.append(u'公司名称')
        elif level == 'store':
            titles.append(u'门店编码')
            titles.append(u'门店名称')
        elif level == 'emp':
            titles.append(u'员工编码')
            titles.append(u'员工姓名')
    if level == u'did':
        titles.append(u'串码')
    else:
        titles.append(u'机器台数')
    titles.append(u'推广数')
    titles.append(u'安装总数')
    return titles


def org_record_to_dict(record, mode, level):
    dict = {
        'total_device_count': record['total_device_count'],
        'did': record['did'] if record.has_key('did') else None,
        'total_popularize_count': record['total_popularize_count'],
        'total_app_count': record['total_app_count'],
        'pici':'1276553gg4',
    }

    empty_value = {'code': '', 'name': ''}
    levels = available_levels(mode, level)
    for level in levels:
        if level == 'region':
            region = utils.get_model_by_pk(Region.objects, record['region'])
            dict['region'] = region.name if region else None
        elif level == 'company':
            company = utils.get_model_by_pk(Company.objects, record['company'])
            if company:
                dict['company'] = { 'code': company.code, 'name': company.name } 
            else:
                dict['company'] = empty_value
        elif level == 'store':
            store = utils.get_model_by_pk(Store.objects, record['store'])
            if store:
                dict['store'] = { 'code': store.code, 'name': store.name } 
            else:
                dict['store'] = empty_value
        elif level == 'emp':
            emp = utils.get_model_by_pk(Employee.objects, record['uid'])
            if emp:
                dict['emp'] = {'username': emp.username, 'realname': emp.realname } 
            else:
                dict['emp'] = {'username': None, 'realname': None}
        else:
            dict['did'] = record['did']
    return dict


@dajaxice_register(method='POST')
@check_login
def filter_org_statistics(request, form, offset, length, mode, level):
    user = cast_staff(request.user)
    form = deserialize_form(form)

    filter_form = OrganizationStatForm(form)
    if not filter_form.is_valid():
        logger.warn("form is invalid")
        logger.warn(filter_form.errors)
        return _invalid_data_json

    logs = filter_org_logs(filter_form, mode)
    aggregate_result = logs.aggregate(capacity=Sum('appCount'))
    logger.debug(aggregate_result)
    capacity = aggregate_result['capacity'] or 0
    levels = available_levels(mode, level)
    keys = [l if l != 'emp' else 'uid' for l in levels]
    records = logs.values(*keys).annotate(total_device_count=Count('did', distinct=True),
                                       total_popularize_count=Sum('popularizeAppCount'),
                                       total_app_count=Sum('appCount'))
    total = records.count()
    devices = sum([i['total_device_count'] for i in records])
    records = records[offset: offset + length]
    items = []
    for record in records:
        items.append(org_record_to_dict(record, mode, level))
    #print [i['total_device_count'] for i in items]

    return simplejson.dumps({
        'ret_code': 0,
        'logs': items,
        'total': total,
        'capacity': capacity,
        'devices': devices
    })
