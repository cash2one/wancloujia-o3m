#coding: utf-8
import logging

from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query import QuerySet
from django.db.models import Q
from django.views.decorators.http import require_GET
from django_tables2.config import RequestConfig

from suning import settings
from suning import permissions
from suning.decorators import active_tab
from mgr.models import cast_staff, Staff, Company, Store, Region
from mgr.forms import *
from mgr.tables import *

logger = logging.getLogger(__name__)

@require_GET
@login_required
@active_tab("account")
def account(request):
    return render(request, "account.html", {
        "account": cast_staff(request.user), 
        "form": ModifyPasswordForm()
    })


def can_view_organization(user):
    if user.is_superuser or user.is_staff:
        return True

    return user.has_perm('mgr.add_organization') or \
            user.has_perm('mgr.change_organization') or \
            user.has_perm('mgr.delete_organization')


def can_add_organization(user):
    if user.is_superuser or user.is_staff:
        return True

    if not user.has_perm("mgr.add_organization"):
        return False

    user = cast_staff(user)
    return user.organization.real_type != ContentType.objects.get_for_model(Store)


def can_add_store(user):
    if user.is_superuser or user.is_staff:
        return True

    if not user.has_perm("mgr.add_organization"):
        return False

    user = cast_staff(user)
    return user.organization.real_type != ContentType.objects.get_for_model(Store)


def can_delete_store(user):
    if user.is_superuser or user.is_staff:
        return True

    if not user.has_perm("mgr.delete_organization"):
        return False

    user = cast_staff(user)
    logger.debug("in store? " + str(user.in_store()))
    return not user.in_store()


@require_GET
@login_required
@user_passes_test(can_view_organization, login_url=settings.PERMISSION_DENIED_URL)
@active_tab("system", "organization")
def organization(request):
    companyForm = CompanyForm()
    storeForm = StoreForm()
    regionForm = RegionForm()

    if request.user.is_superuser or request.user.is_staff:
        store_query_set = Store.objects.all()
        company_query_set = Company.objects.all()
        region_query_set = Region.objects.all()
    else:
        user = cast_staff(request.user)
        organization = user.organization.cast()
        #TODO 直接构造QuerySet
        if organization.real_type == ContentType.objects.get_for_model(Store):
            store = organization
            company = store.parent()
            region = company.parent()
            store_query_set = Store.objects.filter(pk=store.pk)
            company_query_set = Company.objects.filter(pk=company.pk)
            region_query_set = Region.objects.filter(pk=region.pk)
        elif organization.real_type == ContentType.objects.get_for_model(Company):
            company = organization
            region_query_set = Region.objects.filter(pk=company.parent().pk)
            company_query_set = Company.objects.filter(pk=company.pk)
            store_query_set = company.children()
            storeForm.fields["company"].queryset = company_query_set
        else:
            region = organization
            region_query_set = Region.objects.filter(pk=region.pk)
            company_query_set = region.children()
            store_query_set = Store.objects.filter(company__in=company_query_set)
            companyForm.fields["region"].queryset = region_query_set
            storeForm.fields["company"].queryset = company_query_set

    rq = request.GET.get("rq", None)
    if rq:
        region_query_set = region_query_set.filter(name__contains=rq)
    cq = request.GET.get("cq", None)
    if cq:
        company_query_set = company_query_set.filter(Q(code__contains=cq) | Q(name__contains=cq))
    sq = request.GET.get("sq", None)
    if sq:
        store_query_set = store_query_set.filter(Q(code__contains=sq) | Q(name__contains=sq))

    region_query_set = region_query_set.order_by("-pk")

    regionTable = RegionTable(region_query_set)
    storeTable = StoreTable(store_query_set)
    companyTable = CompanyTable(company_query_set)

    if rq:
        regionTable.empty_text = settings.NO_SEARCH_RESULTS
    if cq:
        companyTable.empty_text = settings.NO_SEARCH_RESULTS
    if sq:
        storeTable.empty_text = settings.NO_SEARCH_RESULTS

    RequestConfig(request, paginate={"per_page": 5}).configure(regionTable)
    RequestConfig(request, paginate={"per_page": 5}).configure(companyTable)
    RequestConfig(request, paginate={"per_page": 5}).configure(storeTable)
    return render(request, "organization.html", {
        "cq": cq,
        "sq": sq,
        "rq": rq,
        "companyForm": companyForm,
        "companyTable": companyTable,
        "storeForm": storeForm,
        "storeTable": storeTable,
        'regionForm': regionForm,
        'regionTable': regionTable
    });


@require_GET
@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url=settings.PERMISSION_DENIED_URL)
@active_tab("system", "group")
def group(request):
    query_set = Group.objects.all().order_by("-pk")
    query = request.GET.get("q", None)
    if query:
        query_set = query_set.filter(Q(name__contains=query))

    groupTable = GroupTable(query_set)
    groupForm = GroupForm()
    RequestConfig(request, paginate={"per_page": settings.PAGINATION_PAGE_SIZE}).configure(groupTable)
    return render(request, "group.html", {
        'query': query,
        'groupTable': groupTable,
        'groupForm': groupForm
    }); 


def can_view_staff(user):
    if user.is_superuser or user.is_staff:
        return True

    return user.has_perm('mgr.add_staff') or \
            user.has_perm('mgr.change_staff') or \
            user.has_perm('mgr.delete_staff')

@require_GET
@login_required
@user_passes_test(can_view_staff, login_url=settings.PERMISSION_DENIED_URL)
@active_tab("system", "user")
def user(request):

    if request.user.is_superuser or request.user.is_staff:
        organizations = Organization.objects.all()
        if request.user.is_superuser:
            query_set = Staff.objects.exclude(is_superuser=True)
        else:
            query_set = Employee.objects.all()
    else:
        user = cast_staff(request.user)
        organizations = user.organization.cast().descendants_and_self()
        query_set = Employee.objects.filter(organization__in=organizations)

    query = request.GET.get("q", None)
    if query:
        query_set = query_set.filter(Q(username__contains=query) | 
                                     Q(email__contains=query) | 
                                     Q(realname__contains=query))

    table = StaffTable(query_set)
    employeeForm = EmployeeForm()
    employeeForm.fields["organization"].queryset = organizations
    adminForm = AdminForm()
    resetPasswordForm = ResetPasswordForm()
    RequestConfig(request, paginate={"per_page": settings.PAGINATION_PAGE_SIZE}).configure(table) 

    groupsWidget = None
    permissionsWidget = None
    if request.user.is_superuser or request.user.is_staff:
        groupChoices=[(g.pk, g.name) for g in Group.objects.all()]
        groupChoices.insert(0, ("", "-------"))
        groupsWidget = forms.Select(choices=groupChoices)
        permissionsWidget = forms.SelectMultiple(choices=permissions.get_available_permissions())

    return render(request, "user.html", {
        "table": table,
        "query": query,

        "groupsWidget": groupsWidget,
        "permissionsWidget": permissionsWidget,
        "employeeForm": employeeForm,

        "adminForm": adminForm,
        "resetPasswordForm": resetPasswordForm,
    })

