# coding: utf-8
import logging

from django.utils import simplejson
from django.contrib.auth.models import User
from django.db import models
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form

from interface.models import LogMeta
from app.models import App
from mgr.models import Employee, Organization
from statistics.forms import LogMetaFilterForm
from suning import utils
from suning.decorators import *

logger = logging.getLogger(__name__)

_invalid_data_msg = u'数据出错，请检查'
_invalid_data_json = simplejson.dumps({'ret_code': 1000, 'ret_msg': _invalid_data_msg})
_ok_json = simplejson.dumps({'ret_code': 0})


class UserPermittedFilter:
    def __init__(self, logs, region_id, company_id, store_id, emp_id):
        self.logs = logs
        self.emp_id = emp_id
        self.org_id = utils.first_valid(lambda e: e, [store_id, company_id, region_id])
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


class UserUnpermittedFilter:
    def __init(self, logs, user_id):
        self.logs = logs
        self.user_id = user_id

    def filter(self):
        return self.logs.filter(uid=uid)


class PeriodFilter:
    def __init__(self, logs, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date
        self.logs = logs

    def filter(self):
        logs = self.logs
        if self.from_date:
            from_date = datetime.strftime(from_date) 
            selflogs = logs.filter(date__gte=from_date)

        if self.to_date:
            to_date = datetime.strftime(to_date)
            logs = logs.filter(date__lte=to_date)

        return logs


class BrandFilter:
    def __init__(self, logs, brand):
        self.logs = logs
        self.brand = brand

    def filter(self):
        logs = self.logs
        return logs if not self.brand else logs.filter(brand=self.brand)


@dajaxice_register(method='POST')
@check_login
def get_flow_logs(request, form, offset, length):
    logger.debug("offset: " +  str(offset))
    logger.debug("length: " +  str(length))
    user = request.user
    form = deserialize_form(form)
    logger.debug(form)

    filter_form = LogMetaFilterForm(form)
    if not filter_form.is_valid():
        logger.warn("form is invalid")
        logger.warn(filter_form.errors)
        return _invalid_data_json

    logs = LogMeta.objects.all()
    logger.debug("all logs: %d" % len(logs))
    if user.is_staff or user.is_superuser:
        region_id = filter_form.cleaned_data["region"]
        company_id = filter_form.cleaned_data["company"]
        store_id = filter_form.cleaned_data["store"]
        emp_id = filter_form.cleaned_data["emp"]
        logs = UserPermittedFilter(logs, region_id, company_id, store_id, emp_id).filter()
    else:
        logs = UserUnpermittedFilter(logs, emp_id).filter()
    logger.debug("logs filtered by user info: %d" % len(logs))

    logs = BrandFilter(logs, filter_form.cleaned_data["brand"]).filter()
    logger.debug("logs filtered by brand: %d" % len(logs))

    from_date = filter_form.cleaned_data["from_date"]
    to_date = filter_form.cleaned_data["to_date"]
    logs = PeriodFilter(logs, from_date, to_date).filter()
    logger.debug("logs filtered by period: %d" % len(logs))

    total = len(logs)
    logs = logs[offset: offset + length]

    results = []
    for log in logs:
        item = {
            "brand": log.brand,
            'model': log.model,
            'device': log.did,
            "date": str(log.date)
        }

        apps = App.objects.filter(package=log.appPkg)
        if len(apps) != 0:
            app = apps[0]
            item["app"] = {'id': app.pk, 'package': app.package, 'name': app.name}
            item["popularize"] = app.popularize 
        else:
            item["app"] = {'id': log.appID, 'package': log.appPkg, 'name': ''}
            item["popularize"] = 'undefined'

        emp = utils.get_model_by_pk(Employee.objects, log.uid)
        if not emp:
            item["emp"] = ''
            item["region"] = ''
            item["company"] = ''
            item["store"] = ''
        else:
            item["emp"] = emp.username
            if emp.in_store():
                store = emp.organization.cast()
                company = store.company
                region = company.region
            elif emp.in_company():
                store = None
                company = emp.organization.cast()
                region = company.region
            else:
                store = None
                company = None
                region = emp.organization.cast()
            item["store"] =  store.name if store else ""
            item["company"] = company.name if company else ""
            item["region"] = region.name if region else ""
        results.append(item)
    return simplejson.dumps({
        'ret_code': 0,
        'logs': results,
        'total': total
    })
        

