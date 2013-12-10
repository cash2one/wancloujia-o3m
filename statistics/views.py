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
from suning.utils import render_json, first_valid
from suning.decorators import active_tab
from mgr.models import cast_staff, Region, Company, Store, Organization, Employee
from interface.models import LogMeta
from tables import LogTable
from forms import LogMetaFilterForm

logger = logging.getLogger(__name__)


def _filter_employee_by_organization(organization):
    organizations = organization.descendants_and_self()
    return Employee.objects.filter(organization__in=organizations)

def _filter_logs_by_organization(logs, organization):
    emps = _filter_employee_by_organization(organization)
    pks = emps.values_list('pk', flat=True)
    return logs.filter(uid__in=pks)


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


@require_GET
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
    return render_json(results)


@require_GET
def companies(request):
    user = request.user
    rid = request.GET.get('r', None)
    if not user.is_authenticated() or not rid:
        companies = []
    elif user.is_superuser or user.is_staff:
        companies = Company.objects.filter(region__pk=rid)
    else:
        #TODO
        companies = []

    results = {}
    for c in companies:
        results[str(c.pk)] = c.name
    return render_json(results)


@require_GET
def stores(request):
    user = request.user
    cid = request.GET.get('c', None)

    if not user.is_authenticated() or not cid:
        stores = []
    elif user.is_superuser or user.is_staff:
        stores = Store.objects.filter(company__pk=cid)
    else:
        #TODO
        stores = []
    results = {}
    for s in stores:
        results[str(s.pk)] = s.name
    return render_json(results)

 


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
    logger.debug("%s: admin? %s" %(__name__, str(user.is_superuser or user.is_staff)))

    if user.is_superuser or user.is_staff or \
        user.has_perm("interface.view_organization_statistics"):

        if not user.is_superuser and not user.is_staff:
            logs = _filter_logs_by_organization(user.organization.cast())

        region_id, company_id, store_id = None, None, None
        region_id = query.get('region', None)
        region = _get_model_by_id(Region.objects, region_id) if region_id else None
        if region:
            if user.is_superuser or user.is_staff:
                region_options = {'selected': region.pk, 'items': Region.objects.all()}
            else:
                region_options = {'selected': region.pk, 'items': [region]}
            company_id = query.get('company', None)
            company = _get_model_by_id(Company.objects, company_id) if company_id else None
            if company:
                if user.is_superuser or user.is_staff or user.in_region() or user.in_region():
                    company_options = {'selected': company.pk, 'items': region.children()}
                else:
                    company_options = {'selected': company.pk, 'items': [company]}
                store_id = query.get('store', None)
                store = _get_model_by_id(Store.objects, store_id) if store_id else None
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
        emp = _get_model_by_id(Employee.objects, uid) if uid else None
        filters["user"] = {
            'has_perm': True,
            'region': region_options,
            'company': company_options,
            'store': store_options,
            'username': emp.username if emp else ''
        }
        logger.debug("%s: %s" %(__name__, filters))

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
    return LogMeta.objects.all().values_list('brand', flat=True).distinct()


@require_GET
@login_required
@active_tab("statistics", "flow")
def flow(request):
    return render(request, "flow.html", {
        'brands': _get_brands(),
        'filter': LogMetaFilterForm()
    })


@require_GET
def employee(request):
    if not request.user.is_authenticated():
        return render_json([])

    sid = request.GET.get('s', None)
    cid = request.GET.get('c', None)
    rid = request.GET.get('r', None)
    org_id = first_valid(lambda i: i, [sid, cid, rid])
    if not org_id:
        emps = Employee.objects.all()
    else:
        organization = _get_model_by_id(Organization.objects, org_id)
        logger.debug("organization: " + str(organization))
        emps = _filter_employee_by_organization(organization.cast()) if organization else Employee.objects.all()

    q = request.GET.get("q", "")
    emps = emps.filter(Q(username__contains=q) | Q(email__contains=q) | Q(realname__contains=q))
    emps = emps[0:10]
    results = map(lambda e: {'id': e.pk, 'text': e.username}, emps)
    return render_json({'results': results})

