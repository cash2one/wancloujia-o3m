#coding: utf-8
import logging

from django import forms
from django.utils import simplejson
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query import QuerySet
from django.db.models import Q
from django.views.decorators.http import require_GET, require_POST
from django_tables2.config import RequestConfig
from django.http import HttpResponse

from suning import settings
from suning import permissions
from suning.decorators import active_tab
from mgr.models import cast_staff, Region, Company, Store, Organization, Employee
from interface.models import LogMeta
from tables import LogTable

logger = logging.getLogger(__name__)


def _filter_logs_by_organization(logs, organization):
    organizations = organization.descendants_and_self()
    emps = Employee.objects.filter(organization__in=organizations)
    empids = [emp.pk for emp in emps]
    return logs.filter(uid__in=empids)


def _filter_logs_by_orgs(logs, region_id, company_id, store_id):
    if store_id:
        stores = Store.objects.filter(pk=store_id)
        return [] if len(stores) == 0 else _filter_logs_by_organization(logs, stores[0])

    if company_id:
        companies = Company.objects.filter(pk=company_id)
        return [] if len(companies) == 0 else _filter_logs_by_organization(logs, companies[0])

    if region_id:
        regions = Region.objects.filter(pk=region_id)
        return [] if len(regions) == 0 else _filter_logs_by_organization(logs, regions[0])

    return logs


def _filter_logs_by_period(logs, from_date, to_date):
    if from_date:
        from_date = datetime.strftime(from_date) 
        logs = logs.filter(date__gte=from_date)

    if to_date:
        to_date = datetime.strftime(to_date)
        logs = logs.filter(date__lte=to_date)

    return logs

@require_POST
def regions(request):
    user = request.user
    if not user.is_authenticated():
        regions = []
    elif user.is_superuser or user.is_staff:
        regions = Region.objects.all()
    else:
        user = cast_staff(user)
        regions = [user.get_region()]

    results = {}
    for r in regions:
        results[str(r.pk)] = r.name
    return HttpResponse(simplejson.dumps(results), mimetype='application/json')

@require_POST
def companies(request):
    user = request.user
    rid = request.GET.get('region', None)
    if not user.is_authenticated() or not rid:
        companies = []
    elif user.is_superuser or user.is_staff:
        companies = Company.objects.filter(region__pk=rid)
    else:
        #what?
        companies = []

    results = {}
    for c in companies:
        results[str(c.pk)] = c.name
    return HttpResponse(simplejson.dumps(results), mimetype='application/json')


def _get_model_by_id(manager, id):
    results = manager.filter(pk=id)
    return results[0] if len(results) != 0 else None


def _get_org_by_id(manager, id):
    empty_value = {'pk': '', 'name': ''}
    if not id:
        return empty_value

    results = manager.filter(pk=id)
    return empty_value if len(results) == 0 else results[0]

def _get_emp_by_id(id):
    if not id:
        return {'pk': '', 'username': ''}

    emps = Employee.objects.filter(pk=id)
    return {'pk': '', 'username': ''} if len(emps) == 0 else emps[0]

def _get_app_by_id(id):
    if not id:
        return {'pk': '', 'name': ''}

    apps = App.objects.filter(pk=id)
    return {'pk': '', 'name': ''} if len(apps) == 0 else apps[0]


def _filter_logs_by_user_info(logs, filters, user, query):
    user = cast_staff(user)
    if (user.is_superuser and user.is_staff) or \
        user.has_perm("interface.view_organization_statistics"):

        if not user.is_superuser and not user.is_staff:
            logs = _filter_logs_by_organization(user.organization.cast())

        region_id, company_id, store_id = None, None, None
        region_id = query.get('region', None)
        region = _get_model_by_id(Region.objects, region_id)
        if region:
            if user.is_superuser or user.is_staff:
                region_options = {'selected': region.pk, 'items': Region.objects.all()}
            else:
                region_options = {'selected': region.pk, 'items': [region]}
            company_id = query.get('company', None)
            company = _get_model_by_id(Company.objects, company_id)
            if company:
                if user.is_superuser or user.is_staff or user.in_region() or user.in_region():
                    company_options = {'selected': company.pk, 'items': region.children()}
                else:
                    company_options = {'selected': company.pk, 'items': [company]}
                store_id = query.get('store', None)
                store = _get_model_by_id(Store.objects, store_id)
                if store:
                    if user.is_superuser or user.is_staff or not user.in_store():
                        store_options = {'selected': store.pk, 'items': [company.children()]}
                    else:
                        store_options = {'selected': store.pk, 'items': [store]}
                else:
                    store_options = {'selected': '', 'items': []}
            else:
                company_options = {'selected': '', 'items': []}
                store_options = {'selected': '', 'items': []}
        else:
            region_options = {'selected': '', 'items': []}
            company_options = {'selected': '', 'items': []}
            store_options = {'selected': '', 'items': []}
        uid = query.get('employee', None)
        emp = _get_model_by_id(Employee.objects, uid)
        filters["user"] = {
            'has_perm': True,
            'region': region_options,
            'company': company_options,
            'store': store_options,
            'username': emp.username if emp else ''
        }

        if uid:
            return logs.filter(uid=uid)
        else:
            return _filter_logs_by_orgs(logs, region_id, company_id, store_id)
    else:
        logs = logs.filter(uid=user.pk)
        org = user.organization.cast()
        if org.real_type == ContentType.objects.get_for_model(Region):
            region = org
            company = {'pk': '', 'name': ''}
            store = {'pk': '', 'name': ''}
        elif org.real_type == ConentType.objects.get_for_model(Company):
            region = org.region
            company = org
            store = {'pk': '', 'name': ''}
        else:
            store = org
            company = org.company 
            region = company.region
        filters["user"] = {
            'has_perm': False,
            'region': region,
            'company': company,
            'store': store,
            'username': user.username
        }


def _get_brands():
    return LogMeta.objects.all().values('brand').distinct()


@require_GET
@login_required
@active_tab("statistics", "flow")
def flow(request):
    logs = LogMeta.objects.all()
    filters = {}
    logs = _filter_logs_by_user_info(logs, filters, request.user, request.GET)
    
    appid = request.GET.get('app', None)
    filters["app"] = _get_app_by_id(appid) 
    if appid:
        logs = logs.filter(appID=appid)

    brand = request.GET.get('brand', "")
    filters["brand"] = {
        'selected': brand,
        'items': _get_brands()
    }
    if brand:
        logs = logs.filter(brand=brand)

    from_date = request.GET.get("from_date", "")            
    to_date = request.GET.get("to_date", "")
    filters["period"] = {
        'from_date': from_date,
        'to_date': to_date
    }
    logs = _filter_logs_by_period(logs, from_date, to_date)

    total = len(logs)
    logTable = LogTable(logs)
    RequestConfig(request, paginate={"per_page": 50}).configure(logTable) 
    return render(request, "flow.html", {
        'logTable': logTable,
        'total': total
    })

