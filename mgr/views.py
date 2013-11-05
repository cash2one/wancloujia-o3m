#coding: utf-8
import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query import QuerySet
from django.views.decorators.http import require_GET
from django_tables2.config import RequestConfig

from haystack.query import SearchQuerySet
from mgr.models import cast_staff, Staff, Company, Store
from mgr.forms import *
from mgr.tables import *
from framework.decorators import active_tab

_PAGE_SIZE = 10

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
@user_passes_test(can_view_organization)
@active_tab("system", "organization")
def organization(request):
    companyForm = CompanyForm()
    storeForm = StoreForm()
    if request.user.is_superuser or request.user.is_staff:
        companyTable = CompanyTable(Company.objects.all())
        storeTable = StoreTable(Store.objects.all())
    else:
        user = cast_staff(request.user)
        organization = user.organization.cast()
        if organization.real_type == ContentType.objects.get_for_model(Store):
            store = organization
            company = store.company
            #TODO 直接构造QuerySet
            companyTable = CompanyTable(Company.objects.filter(pk=company.pk))
            storeTable = StoreTable(Store.objects.filter(pk=store.pk))
        else:
            company = organization.cast()
            #TODO 直接构造QuerySet
            companyTable = CompanyTable(Company.objects.filter(pk=company.pk))
            storeTable = StoreTable(Store.objects.filter(company=company))

    RequestConfig(request, paginate={"per_page": 5}).configure(companyTable)
    RequestConfig(request, paginate={"per_page": 5}).configure(storeTable)
    return render(request, "organization.html", {
        "companyForm": companyForm,
        "companyTable": companyTable,
        "storeForm": storeForm,
        "storeTable": storeTable
    });


@require_GET
@login_required
@active_tab("system", "group")
def group(request):
    groupTable = GroupTable(Group.objects.all().order_by("-pk"))
    groupForm = GroupForm()
    RequestConfig(request, paginate={"per_page": _PAGE_SIZE}).configure(groupTable)
    return render(request, "group.html", {
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
@user_passes_test(can_view_staff)
@active_tab("system", "user")
def user(request):
    organizations = Organization.objects.all()
    if request.user.is_superuser:
        query_set = Staff.objects.all()
    elif request.user.is_staff:
        query_set = Employee.objects.all()
    else:
        user = cast_staff(request.user)
        if user.in_store():
            query_set = Employee.objects.filter(organization=user.organization)
            organizations = Organization.objects.filter(pk=user.organization.pk)
        else:
            company = user.organization
            stores = Store.objects.filter(company=company)
            organization_pks = [store.pk for store in stores]
            organization_pks.append(company.pk)
            organizations = Organization.objects.filter(pk__in=organization_pks)
            query_set = Employee.objects.filter(organization__pk__in=organization_pks)

    logger.debug(organizations)
    table = StaffTable(query_set)
    employeeForm = EmployeeForm()
    employeeForm.fields["organization"].queryset = organizations
    adminForm = AdminForm()
    resetPasswordForm = ResetPasswordForm()
    RequestConfig(request, paginate={"per_page": _PAGE_SIZE}).configure(table)
    return render(request, "user.html", {
        "table": table,
        "employeeForm": employeeForm,
        "adminForm": adminForm,
        "resetPasswordForm": resetPasswordForm
    })

