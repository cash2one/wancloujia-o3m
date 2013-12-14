# coding: utf-8
import logging
from datetime import datetime

from django.utils import simplejson
from django.contrib.auth.models import User
from django.db import models
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form

from interface.models import LogMeta
from app.models import App
from mgr.models import Employee, Organization, cast_staff
from statistics.forms import LogMetaFilterForm, InstalledAppLogEntity
from suning import utils
from suning.decorators import *


logger = logging.getLogger(__name__)
_invalid_data_msg = u'数据出错，请检查'
_invalid_data_json = simplejson.dumps({'ret_code': 1000, 'ret_msg': _invalid_data_msg})
_ok_json = simplejson.dumps({'ret_code': 0})


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

def log_to_dict(log):
    dict = {
        'brand': log.brand,
        'model': log.model,
        'device': log.did,
        'date': str(log.date)
    }

    apps = App.objects.filter(package=log.appPkg)
    app = apps[0] if len(apps) != 0 else None
    dict["app"] = {
        'id': app.pk if app else log.appID, 
        'package': app.package if app else log.appPkg,
        'name': app.name if app else None,
        'popularize': app.popularize if app else None
    }

    emp = utils.get_model_by_pk(Employee.objects, log.uid)
    organizations = [None, None, None]
    if emp:
        dict["emp"] = emp.username
        for i, item in enumerate(emp.organizations()):
            organizations[i] = item.name
    else:
        dict["emp"] = None
    dict["region"], dict["company"], dict["store"] = organizations

    return dict;

    
def filter_flow_logs(user, form):
    logs = LogMeta.objects.all().order_by('-date')
    logger.debug("all logs: %d" % len(logs))

    region_id = form.cleaned_data["region"]
    company_id = form.cleaned_data["company"]
    store_id = form.cleaned_data["store"]
    emp_id = form.cleaned_data["emp"]
    if user.is_staff or user.is_superuser:
        logs = AdminFilter(logs, region_id, company_id, store_id, emp_id).filter()
    elif user.has_perm("interface.view_organization_statistics"):
        logs = UserPermittedFilter(user, logs, region_id, company_id, store_id, emp_id).filter()
    else:
        logs = UserUnpermittedFilter(logs, request.user.pk).filter()
    logger.debug("logs filtered by user info: %d" % len(logs))

    logs = AppFilter(logs, form.cleaned_data["app"]).filter()
    logger.debug("logs filtered by app: %d" % len(logs))

    logs = BrandFilter(logs, form.cleaned_data["brand"]).filter()
    logger.debug("logs filtered by brand: %d" % len(logs))

    from_date = form.cleaned_data["from_date"]
    to_date = form.cleaned_data["to_date"]
    logs = PeriodFilter(logs, from_date, to_date).filter()
    logger.debug("logs filtered by period: %d" % len(logs))
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
    total = len(logs)
    logs = logs[offset: offset + length]
    dict_list = []
    for log in logs:
        dict_list.append(log_to_dict(log))

    return simplejson.dumps({
        'ret_code': 0,
        'logs': dict_list,
        'total': total
    })           


def filter_installed_capacity_logs(user, form):
    logs = InstalledAppLogEntity.objects.all().order_by('-date')
    logger.debug("all logs: %d" % len(logs))

    region_id = form.cleaned_data["region"]
    company_id = form.cleaned_data["company"]
    store_id = form.cleaned_data["store"]
    emp_id = form.cleaned_data["emp"]
    if user.is_staff or user.is_superuser:
        logs = AdminFilter(logs, region_id, company_id, store_id, emp_id).filter()
    elif user.has_perm("interface.view_organization_statistics"):
        logs = UserPermittedFilter(user, logs, region_id, company_id, store_id, emp_id).filter()
    else:
        logs = UserUnpermittedFilter(logs, request.user.pk).filter()
    logger.debug("logs filtered by user info: %d" % len(logs))

    logs = AppFilter(logs, form.cleaned_data["app"]).filter()
    logger.debug("logs filtered by app: %d" % len(logs))

    logs = BrandFilter(logs, form.cleaned_data["brand"]).filter()
    logger.debug("logs filtered by brand: %d" % len(logs))

    from_date = form.cleaned_data["from_date"]
    to_date = form.cleaned_data["to_date"]
    logs = PeriodFilter(logs, from_date, to_date).filter()
    logger.debug("logs filtered by period: %d" % len(logs))
    return logs


'''

@dajaxice_register(method='POST')
@check_login
def get_installed_capacity(request, form, offset, length):
    user = cast_staff(request.user)
    form = deserialize_form(form)

    filter_form = LogMetaFilterForm(form)
    if not filter_form.is_valid():
        logger.warn("form is invalid")
        logger.warn(filter_form.errors)
        return _invalid_data_json

    logs = filter_flow_logs(user, filter_form)
    total = len(logs)
    logs = logs[offset: offset + length]
    dict_list = []
    for log in logs:
        dict_list.append(log_to_dict(log))

    return simplejson.dumps({
        'ret_code': 0,
        'logs': dict_list,
        'total': total
    })

'''
