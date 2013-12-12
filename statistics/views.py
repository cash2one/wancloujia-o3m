#coding: utf-8
import logging
import datetime
import math

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
from suning.utils import render_json, first_valid, get_model_by_pk
from suning.decorators import active_tab
from mgr.models import cast_staff, Region, Company, Store, Organization, Employee
from app.models import App
from interface.models import LogMeta
from forms import LogMetaFilterForm

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


def _get_brands():
    return LogMeta.objects.all().values_list('brand', flat=True).distinct()


@require_GET
@login_required
@active_tab("statistics", "flow")
def flow(request):
    today = datetime.date.today()
    first_day = datetime.date(today.year, today.month, 1)
    user = cast_staff(request.user)
    user_filter = { 
        'region': { 'disabled': False },
        'company': { 'disabled': False },
        'store': { 'disabled': False },
        'emp': { 'disabled': False }
    }

    if not user.is_superuser and not user.is_staff:
        organizations = [None, None, None]
        for i, org in enumerate(user.organizations()):
            organizations[i] = org

        user_filter["region"]["value"] = organizations[0] 
        user_filter["region"]["disabled"] = organizations[0] is not None

        user_filter["company"]["value"] = organizations[1] 
        user_filter["company"]["disabled"] = organizations[1] is not None

        user_filter["store"]["value"] = organizations[2]
        user_filter["store"]["disabled"] = organizations[1] is not None


        if not user.has_perm("interface.view_organization_statistics"):
            user_filter["region"]["disabled"] = True
            user_filter["company"]["disabled"] = True
            user_filter["region"]["disabled"] = True
            user_filter["emp"]["disabled"] = True

        user_filter["emp"]["value"] = user
        
    return render(request, "flow.html", {
        'brands': _get_brands(),
        'user_filter': user_filter,
        'first_day': str(first_day),
        'today': str(today),
        'filter': LogMetaFilterForm()
    })


def query_employee(user, org):
    if not org:
        return Employee.objects.none()

    if user.is_superuser or user.is_staff or org.belong_to(user.org()):
        return Employee.filter_by_organization(org)
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
        not user.has_perm("interface.view_orgnaization_statistics"):
        emps = Employee.objects.filter(pk=user.pk)
        return render_json({'results': emps_to_dict_arr(emps)})

    sid = request.GET.get('s', None)
    cid = request.GET.get('c', None)
    rid = request.GET.get('r', None)
    org_id = first_valid(lambda i: i, [sid, cid, rid])
    org = get_model_by_pk(Organization.objects, org_id) if org_id else None
    org = org.cast() if org else None

    if not org:
        return render_json({'results': emps_to_dict_arr(Employee.objects.none())})

    emps = query_employee(user, org)
    q = request.GET.get("q", "")
    emps = Employee.query(emps, q)
    emps = emps[0:10]
    results = map(lambda e: {'id': e.pk, 'text': e.username}, emps)
    return render_json({'results': results})


@require_GET
def apps(request):
    if not request.user.is_authenticated():
        return render_json([])

    q = request.GET.get('q', "")
    p = request.GET.get('p', "")
    page = int(p) if p else 0

    APPS_PER_PAGE = 10
    apps = App.objects.filter(name__contains=q)
    total = len(apps)
    pages = int(math.ceil(total/float(APPS_PER_PAGE))) 

    apps = apps[(page-1)*APPS_PER_PAGE:page*APPS_PER_PAGE]
    results = map(lambda e: {'id': e.pk, 'text': e.name}, apps)

    return render_json({'more': pages > page, 'results': results})


