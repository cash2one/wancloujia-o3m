# coding: utf-8
import logging

from django.utils import simplejson
from django.contrib.auth.models import User
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form

from framework.decorators import request_delay, check_login, response_error
from forms import *
from models import *
from decorators import preprocess_form

logger = logging.getLogger(__name__)

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
    user.save()
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
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'用户名重名'})
        admin.set_password(Staff.DEFAULT_PASSWORD)
        admin.save()
        return _ok_json
    else:
        id = form["id"]
        if User.objects.exclude(pk=id).filter(username=admin.username).exists():
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'用户名重名'})
        admin.pk = id 
        #fixme
        admin.password = Administrator.objects.get(pk=id).password
        admin.save()
        return _ok_json


@dajaxice_register(method='POST')
@check_login
@preprocess_form
def add_edit_employee(request, form):
    f = EmployeeForm(form)
    if not f.is_valid():
        logger.warn("add_edit_employee: form is invalid")
        logger.warn(f.errors)
        return _invalid_data_json

    employee = f.save(commit=False)
    if form["id"] == '':
        if User.objects.filter(username=employee.username).exists():
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'用户名重名'})
        employee.set_password(Staff.DEFAULT_PASSWORD)
        employee.save()
        f.save_m2m()
        return _ok_json
    else:
        id = form["id"]
        if User.objects.exclude(pk=id).filter(username=employee.username).exists():
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'用户名重名'})
        employee.pk = id
        #fixme
        employee.password = Employee.objects.get(pk=id).password
        employee.save()
        f.save_m2m()
        return _ok_json


@dajaxice_register(method='POST')
@check_login
@preprocess_form
def add_edit_company(request, form):
    f = CompanyForm(form)
    if not f.is_valid():
        logger.warn("add_edit_company: data is invalid")
        logger.warn(f.errors)
        return _invalid_data_json

    company = f.save(commit=False)
    #fixme 想法让CompanyForm与add_edit_company解耦，取消下面的赋值
    company.code = f.cleaned_data["code"]
    if form["id"] == '':
        if Company.objects.filter(code=company.code).exists():
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'公司编码重复'})
        company.save()
        return _ok_json
    else:
        id = form["id"]
        if Company.objects.exclude(pk=id).filter(code=company.code).exists():
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'公司编码重复'})
        company.pk = id
        company.save()
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
    if form["id"] == '':
        if Store.objects.filter(code=store.code).exists():
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'门店编码重复'})
        store.save()
        return _ok_json
    else:
        id = form["id"]
        if Store.objects.exclude(pk=id).filter(code=store.code).exists():
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'门店编码重复'})
        store.pk = id 
        store.save()
        return _ok_json

@dajaxice_register(method='POST')
@check_login
def delete_organization(request, id):
    Organization.objects.get(pk=id).delete()
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def delete_user(request, id):
    User.objects.get(pk=id).delete()
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
            logger.debug("name: " + group.name)
            logger.debug("exists? " + str(Group.objects.filter(name=group.name).exists()))
            logger.debug("groups: "  + ", ".join([g.name for g in Group.objects.filter(name=group.name)]))
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'用户组名已存在'})
        group.save()    
        f.save_m2m()
        return _ok_json
    else:
        id = form["id"]
        if Group.objects.exclude(pk=id).filter(name=group.name).exists():
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'用户组名已存在'})
        group.pk = id;
        group.save()
        f.save_m2m()
        return _ok_json


@dajaxice_register(method='POST')
@check_login
def delete_group(request, id):
    Group.objects.get(pk=id).delete()
    return _ok_json

