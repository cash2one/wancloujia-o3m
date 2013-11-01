#coding: utf-8
import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django_tables2.config import RequestConfig

from haystack.query import SearchQuerySet
from mgr.models import cast_staff, Staff, Company, Store
from mgr.forms import ModifyPasswordForm, ResetPasswordForm, EmployeeForm, AdminForm, CompanyForm, StoreForm
from mgr.tables import StaffTable, CompanyTable, StoreTable
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


@require_GET
@login_required
@active_tab("system", "organization")
def organization(request):
    #FIXME 限制普通用户的编辑范围
    companyForm = CompanyForm()
    storeForm = StoreForm()
    companyTable = CompanyTable(Company.objects.all())
    storeTable = StoreTable(Store.objects.all())
    RequestConfig(request, paginate={"per_page": 5}).configure(companyTable)
    RequestConfig(request, paginate={"per_page": 5}).configure(storeTable)
    return render(request, "organization.html", {
        "companyForm": companyForm,
        "companyTable": companyTable,
        "storeForm": storeForm,
        "storeTable": storeTable
    });


@login_required
@require_GET
@active_tab("system", "user")
def user(request):
    #FIXME 根据用户可管理的员工信息的范围进行过滤
    query_set = Staff.objects.exclude(is_superuser=True)
    table = StaffTable(query_set)
    employeeForm = EmployeeForm()
    adminForm = AdminForm()
    resetPasswordForm = ResetPasswordForm()
    RequestConfig(request, paginate={"per_page": _PAGE_SIZE}).configure(table)
    return render(request, "user.html", {
        "table": table,
        "employeeForm": employeeForm,
        "adminForm": adminForm,
        "resetPasswordForm": resetPasswordForm
    })

