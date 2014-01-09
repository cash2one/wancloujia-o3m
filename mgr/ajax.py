# coding: utf-8
import logging
import random

import redis
from django.utils import simplejson
from django.contrib.auth.models import User, Group, Permission
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form
from suning import settings

from suning.decorators import *
from suning.service import notify
from forms import *
from models import *

logger = logging.getLogger(__name__)

_DEFAULT_PASSWORD= '123456'
_invalid_data_msg = u'数据出错，请检查'
_invalid_data_json = simplejson.dumps({'ret_code': 1000, 'ret_msg': _invalid_data_msg})
_ok_json = simplejson.dumps({'ret_code': 0})


#@request_delay(3)
@dajaxice_register(method='POST')
#@response_error
@check_login
@preprocess_form
def modify_password(request, form):
    f = ModifyPasswordForm(form)
    if not f.is_valid():
        logger.debug('modify_password: form is invalid')
        return _invalid_data_json;

    user = request.user
    origin = f.cleaned_data["origin"]
    if not user.check_password(origin):
        logger.debug("password not match, param: %s", origin)
        ret_msg = u'密码不正确，请重新填写'
        return simplejson.dumps({'ret_code': 1000, 'ret_msg': ret_msg})

    password = f.cleaned_data["password"]
    user.set_password(password)
    if user.is_superuser or user.is_staff:
        __mod_adminpass(user, request.user.username)
    else:
        __mod_pass(user, request.user.username)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
@preprocess_form
def reset_password(request, form):
    f = ResetPasswordForm(form)
    if not f.is_valid():
        logger.warn("reset_password: form is invalid")
        logger.warn(f.errors)
        return _invalid_data_json

    logger.debug("password: " + f.cleaned_data["password"])
    user = User.objects.get(pk=form["id"])
    user.set_password(f.cleaned_data["password"])
    user.save()
    return _ok_json


@dajaxice_register(method='POST')
@check_login
@preprocess_form
def add_edit_admin(request, form):
    f = AdminForm(form)
    if not f.is_valid():
        logger.warn("add_edit_admin: form is invalid")
        logger.warn(f.errors)
        return _invalid_data_json

    admin = f.save(commit=False)
    if form["id"] == '':
        if User.objects.filter(username=admin.username).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'username', 'error': u'用户名重名'})
        #password = str(random.randrange(100000, 999999))
        password = _DEFAULT_PASSWORD
        admin.set_password(password)
        __add_admin(admin, request.user.username)
        #notify(admin, password)
        return _ok_json
    else:
        id = form["id"]
        if User.objects.exclude(pk=id).filter(username=admin.username).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'username', 'error': u'用户名重名'})
        admin.pk = id 
        #fixme
        admin.password = Administrator.objects.get(pk=id).password
        __edit_admin(admin, request.user.username)
        return _ok_json


def _modify_groups_and_permissions(id, groups, permissions):
    employee = Employee.objects.get(pk=id)
    logger.debug("%s groups: %s" % (__name__, groups))
    logger.debug("%s permissions: %s" % (__name__, permissions))
    employee.groups=Group.objects.filter(pk__in=groups)
    employee.user_permissions=Permission.objects.filter(pk__in=permissions)
    employee.save()
    logger.debug("%s employee.permissions: %s" % (__name__, employee.user_permissions.all()))
    logger.debug("%s employee.groups: %s" % (__name__, employee.groups.all()))


@dajaxice_register(method='POST')
@check_login
def add_edit_employee(request, form, permissions):
    form = deserialize_form(form)
    logger.debug("form: " + str(map(lambda k: (k, form[k]), form)))
    logger.debug("permissions:" + permissions)

    f = EmployeeForm(form)
    if not f.is_valid():
        logger.warn("add_edit_employee: form is invalid")
        logger.warn(f.errors)
        return _invalid_data_json

    employee = f.save(commit=False)
    if form["id"] == '':
        if User.objects.filter(username=employee.username).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'username', 'error': u'工号重复'})
        #password = str(random.randrange(100000, 999999))
        password = _DEFAULT_PASSWORD
        employee.set_password(password)
        __add_user(employee, request.user.username)
        #notify(employee, password)
    else:
        id = form["id"]
        if User.objects.exclude(pk=id).filter(username=employee.username).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'username', 'error': u'工号重复'})
        employee.pk = id
        #fixme
        employee.password = Employee.objects.get(pk=id).password
        __edit_user(employee, request.user.username)

    if not request.user.is_staff and not request.user.is_superuser:
        return _ok_json

    if permissions is not None and form.has_key("groups"):
        logger.debug("modify employee's groups and permissions")
        groups = form["groups"]
        permissions = [int(p) for p in permissions.split(",")] if permissions else []
        groups = [int(g) for g in groups.split(",")] if groups else []
        _modify_groups_and_permissions(employee.pk, groups, permissions)
        return _ok_json


@dajaxice_register(method='POST')
@check_login
@preprocess_form
def add_edit_region(request, form):
    f = RegionForm(form)
    if not f.is_valid():
        logger.warn("%s: data is invalid" % __name__)
        logger.warn(f.errors)
        return _invalid_data_json

    if form["id"] == '':
        region = Region(name=f.cleaned_data["name"])
        if Region.objects.filter(name=region.name).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'name', 'error': u'大区名已存在'})
        __add_region(region, request.user.username)
    else:
        region = Region.objects.get(pk=form["id"])
        region.name = f.cleaned_data["name"]
        if Region.objects.exclude(pk=region.pk).filter(name=region.name).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'name', 'error': u'大区名已存在'})
        __edit_region(region, request.user.username)

    return _ok_json


@dajaxice_register(method='POST')
#@request_delay(3)
@check_login
@preprocess_form
def add_edit_company(request, form):
    f = CompanyForm(form)
    if not f.is_valid():
        logger.warn("add_edit_company: data is invalid")
        logger.warn(f.errors)
        return _invalid_data_json

    company = f.save(commit=False)
    company.code = f.cleaned_data["code"]
    company.name = f.cleaned_data["name"]

    if form["id"] == '':
        if Company.objects.filter(code=company.code).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'code', 'error': u'公司编码重复'})
        if Company.objects.filter(name=company.name).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'name', 'error': u'公司名已存在'})
        __add_company(company, request.user.username)
    else:
        id = form["id"]
        if Company.objects.exclude(pk=id).filter(code=company.code).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'code', 'error': u'公司编码重复'})
        if Company.objects.exclude(pk=id).filter(name=company.name).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'name', 'error': u'公司名已存在'})
        company.pk = id
        __edit_company(company, request.user.username)

    return _ok_json


@dajaxice_register(method='POST')
@check_login
@preprocess_form
def add_edit_store(request, form):
    f = StoreForm(form)
    if not f.is_valid():
        logger.warn("add_edit_store: form is invalid")
        logger.warn(f.errors)
        return _invalid_data_json

    store = f.save(commit=False)
    store.code = f.cleaned_data["code"]
    store.name = f.cleaned_data["name"]

    if form["id"] == '':
        if Store.objects.filter(code=store.code).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'code', 'error': u'门店编码重复'})
        if Store.objects.filter(name=store.name).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'name', 'error': u'门店名已存在'})
        __add_store(store, request.user.username)
    else:
        id = form["id"]
        if Store.objects.exclude(pk=id).filter(code=store.code).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'code', 'error': u'门店编码重复'})
        if Store.objects.exclude(pk=id).filter(name=store.name).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'name', 'error': u'门店名已存在'})
        store.pk = id 
        __edit_store(store, request.user.username)
        
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def delete_organization(request, id):
    model = Organization.objects.get(pk=id)
    model = model.cast()
    model.delete()
    if type(model) == Region:
        __remove_region(model, request.user.username)
    elif type(model) == Company:
        __remove_company(model, request.user.username)
    elif type(model) == Store:
        __remove_store(model, request.user.username)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def delete_user(request, id):
    model = User.objects.get(pk=id)
    __remove_user(model, request.user.username)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
@preprocess_form
def add_edit_group(request, form):
    f = GroupForm(form)
    if not f.is_valid():
        logger.warn("%s: form is invalid" % __name__)
        logger.warn(f.errors)
        return _invalid_data_json

    group = f.save(commit=False)
    group.name = f.cleaned_data["name"]
    if form["id"] == '':
        if Group.objects.filter(name=group.name).exists():
            logger.debug("group name exists, name: " + group.name)
            return simplejson.dumps({'ret_code': 1000, 'field': 'name', 'error': u'用户组名已存在'})
        group.save()    
        f.save_m2m()
        __add_group(group, request.user.username)
        return _ok_json
    else:
        id = form["id"]
        if Group.objects.exclude(pk=id).filter(name=group.name).exists():
            logger.debug("group name exists, name: " + group.name)
            return simplejson.dumps({'ret_code': 1000, 'field': 'name', 'error': u'用户组名已存在'})
        group.pk = id;
        group.save()
        f.save_m2m()
        __edit_group(group, request.user.username)
        return _ok_json


@dajaxice_register(method='POST')
@check_login
def delete_group(request, id):
    model = Group.objects.get(pk=id)
    __remove_group(model, request.user.username)
    return _ok_json


def __add_region(model, username):
    model.save()
    oplogtrack(15, username, model)

def __edit_region(model, username):
    model.save()
    oplogtrack(16, username, model)

def __remove_region(model, username):
    oplogtrack(17, username, model)

def __add_company(model, username):
    model.save()
    oplogtrack(18, username, model)

def __edit_company(model, username):
    model.save()
    oplogtrack(19, username, model)

def __remove_company(model, username):
    oplogtrack(20, username, model)

def __add_store(model, username):
    model.save()
    oplogtrack(21, username, model)

def __edit_store(model, username):
    model.save()
    oplogtrack(22, username, model)

def __remove_store(model, username):
    oplogtrack(23, username, model)

def __add_group(model, username):
    oplogtrack(24, username, model)

def __edit_group(model, username):
    oplogtrack(25, username, model)

def __remove_group(model, username):
    model.delete()
    oplogtrack(26, username, model)

def __add_user(model, username):
    model.save()
    oplogtrack(27, username, model)

def __edit_user(model, username):
    model.save()
    oplogtrack(28, username, model)

def __remove_user(model, username):
    model.delete()
    oplogtrack(29, username, model)

def __mod_pass(model, username):
    model.save()
    oplogtrack(30, username, model)

def __add_admin(model, username):
    model.save()
    oplogtrack(31, username, model)

def __edit_admin(model, username):
    model.save()
    oplogtrack(32, username, model)

def __remove_admin(model, username):
    oplogtrack(33, username, model)

def __mod_adminpass(model, username):
    oplogtrack(34, username, model)