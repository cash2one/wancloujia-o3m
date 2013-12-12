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


@require_GET
def regions(request):
    user = request.user
    if not user.is_authenticated():
        regions = []
    elif user.is_superuser or user.is_staff:
        regions = Region.objects.all()
    else:
        user = cast_staff(user)
        regions = [user.organizations()[0]]

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
        user = cast_staff(user)
        companies = [] if user.in_region() >= 2 else user.organizations()[1]

    results = {}
    for c in companies:
        results[str(c.pk)] = "%s%s" % (c.code, c.name)
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
        user = cast_staff(user)
        stores = [user.org()] if user.in_store() else []

    results = {}
    for s in stores:
        results[str(s.pk)] = "%s%s" % (s.code, s.name)
    return render_json(results)


def _get_brands():
    return LogMeta.objects.all().values_list('brand', flat=True).distinct()


@require_GET
@login_required
@active_tab("statistics", "flow")
def flow(request):
    today = datetime.date.today()
    first_day = datetime.date(today.year, today.month, 1)
    user = cast_staff(request.user)
    user_filter = {'has_perm': True}
    if not user.is_superuser and not user.is_staff and \
        not user.has_perm("interface.view_organization_statistics"):
        user_filter["has_perm"] = False
        organizations = [None, None, None]
        for i, org in enumerate(user.organizations()):
            organizations[i] = org
        user_filter["region"], user_filter["company"], user_filter["store"] = organizations
        user_filter["emp"] = user
        
    return render(request, "flow.html", {
        'brands': _get_brands(),
        'user_filter': user_filter,
        'first_day': str(first_day),
        'today': str(today),
        'filter': LogMetaFilterForm()
    })


@require_GET
def employee(request):
    if not request.user.is_authenticated():
        return render_json([])

    user = cast_staff(request.user)
    if not user.is_superuser and not user.is_staff and \
        not user.has_perm("interface.view_orgnaization_statistics")
        emps = [user]
    else:
        sid = request.GET.get('s', None)
        cid = request.GET.get('c', None)
        rid = request.GET.get('r', None)
        org_id = first_valid(lambda i: i, [sid, cid, rid])
        org = get_model_by_pk(Organization.objects, org_id) if org_id else None
        org = org.cast if org else None
        if user.is_superuser or user.is_staff:
            emps = Employee.objects.all()
            if org:
                emps = Employee.filter_by_organization(emps, org)
        else:
            if org and org.belong_to(user.org()):
                # TODO 自定义ModelManager
                emps = Employee.filter_by_organization(Employee.objects.all(), org)
            else:
                emps = []

        if not org_id:
            emps = Employee.objects.all()
        else:
            logger.debug("organization: " + str(organization))
            if organization
                    q = request.GET.get("q", "")
        emps = emps.filter(Q(username__contains=q) | Q(email__contains=q) | Q(realname__contains=q))
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


