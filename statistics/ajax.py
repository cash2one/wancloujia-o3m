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
from statistics.forms import LogMetaFilterForm
from suning.settings import EMPTY_VALUE
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

        return LogMeta.filter_by_organization(self.logs, org.cast())


class UserPermittedFilter(AdminFilter):
    def __init__(self, user, logs, region_id, company_id, store_id, emp_id):
        AdminFiler.__int__(self, logs, region_id, company_id, store_id, emp_id)
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
            if org and org.belong_to(user_log):
                return LogMeta.filter_by_organization(self.logs, org)
            else:
                return self.logs.none()

        return LogMeta.filter_by_organization(self.logs, user_org)


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


def _logs_to_dict_array(logs):
    results = []
    for log in logs:
        dict = {
            "brand": log.brand or EMPTY_VALUE,
            'model': log.model or EMPTYP_VALUE,
            'device': log.did or EMPTY_VALUE,
            "date": str(log.date)
        }

        apps = App.objects.filter(package=log.appPkg)
        if len(apps) != 0:
            app = apps[0]
            dict["app"] = {'id': app.pk, 'package': app.package, 'name': app.name}
            dict["popularize"] = app.popularize 
        else:
            dict["app"] = {'id': log.appID, 'package': log.appPkg, 'name': EMPTY_VALUE}
            dict["popularize"] = 'undefined'

        organizations = [EMPTY_VALUE, EMPTY_VALUE, EMPTY_VALUE]
        emp = utils.get_model_by_pk(Employee.objects, log.uid)
        if emp:
            for i, item in enumerate(emp.organizations()):
                organizations[i] = item.name
            dict["emp"] = emp.username
        else:
            dict["emp"] = EMPTY_VALUE
                
        dict["region"], dict["company"], dict["store"] = organizations
        results.append(dict)
    return results


@dajaxice_register(method='POST')
@check_login
def get_flow_logs(request, form, offset, length):
    user = cast_staff(request.user)
    form = deserialize_form(form)
    logger.debug(form)

    filter_form = LogMetaFilterForm(form)
    if not filter_form.is_valid():
        logger.warn("form is invalid")
        logger.warn(filter_form.errors)
        return _invalid_data_json

    logs = LogMeta.objects.all().order_by('-date')
    logger.debug("all logs: %d" % len(logs))

    region_id = filter_form.cleaned_data["region"]
    company_id = filter_form.cleaned_data["company"]
    store_id = filter_form.cleaned_data["store"]
    emp_id = filter_form.cleaned_data["emp"]
    if user.is_staff or user.is_superuser:
        logs = AdminFilter(logs, region_id, company_id, store_id, emp_id).filter()
    elif user.has_perm("interface.view_organization_statistics"):
        logs = UserPermittedFilter(user, logs, region_id, company_id, store_id, emp_id).filter()
    else:
        logs = UserUnpermittedFilter(logs, emp_id).filter()
    logger.debug("logs filtered by user info: %d" % len(logs))

    logs = AppFilter(logs, filter_form.cleaned_data["app"]).filter()
    logger.debug("logs filtered by app: %d" % len(logs))

    logs = BrandFilter(logs, filter_form.cleaned_data["brand"]).filter()
    logger.debug("logs filtered by brand: %d" % len(logs))

    from_date = filter_form.cleaned_data["from_date"]
    to_date = filter_form.cleaned_data["to_date"]
    logs = PeriodFilter(logs, from_date, to_date).filter()
    logger.debug("logs filtered by period: %d" % len(logs))

    total = len(logs)
    logs = logs[offset: offset + length]
    return simplejson.dumps({
        'ret_code': 0,
        'logs': _logs_to_dict_array(logs),
        'total': total
    })           

