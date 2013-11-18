# coding: utf-8
import logging
import time
from datetime import datetime

from django.utils import simplejson
from django.contrib.auth.models import User
from dajaxice.decorators import dajaxice_register

from suning.decorators import request_delay
from forms import *
from suning.decorators import *
from app import models

logger = logging.getLogger(__name__)

_invalid_data_msg = u'数据出错，请检查'
_invalid_data_json = simplejson.dumps({'ret_code': 1000, 'ret_msg': _invalid_data_msg})
_ok_json = simplejson.dumps({'ret_code': 0})

@dajaxice_register(method='POST')
@check_login
@preprocess_form
def add_edit_app(request, form):
    f = AppForm(form)
    if not f.is_valid():
        logger.warn("%s: form is invalid" % __name__)
        logger.warn(f.errors)
        return _invalid_data_json

    if form["app_icon"] == "" or form["app_icon"] is None:
        return simplejson.dumps({'ret_code': 1000, 'field': 'app_icon', 'error': u'应用图标必须上传'})

    logger.debug(models)
    app = f.save(commit=False)
    app.name = form["name"]
    app.package = form["package"]
    app.app_icon = form["app_icon"]
    if form["id"] == "":
        if models.App.objects.filter(package=app.package).exists():
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'应用已存在'})
        app.online = True
        app.save()
    else:
        app.pk = form["id"]
        if models.App.objects.get(pk=app.pk).package != app.package:
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'应用包名不相同'})
        app.create_date = models.App.objects.get(pk=app.pk).create_date
        app.save()

    return _ok_json


@dajaxice_register(method='POST')
@check_login
def delete_app(request, id):
    models.App.objects.get(pk=id).delete()
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def publish_app(request, id):
    models.App.objects.filter(pk=id).update(online=True)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def drop_app(request, id):
    models.App.objects.filter(pk=id).update(online=False)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
@preprocess_form
def add_edit_subject(request, form):
    name = form["name"]
    pk = form["id"]
    cover = form["cover"]
    desc = form["desc"] 
    apps = form["apps"]

    if not name or not cover or not apps:
        logger("%s: param is invalid", __name__)
        return _invalid_data_json

    apps = [int(item) for item in form["apps"].split(",")]
    if pk == "":
        subject = Subject(name=name, cover=cover, desc=desc)
        if models.Subject.objects.filter(name=subject.name).exists():
            return simplejson.dumps({
                'ret_code': 1000, 
                'field': 'name', 
                'error': u'应用专题名已存在' 
            })
        models.add_subject(subject, apps, request.user)
    else:
        subject = Subject.objects.get(pk=int(pk))
        subject.name = name
        subject.cover = cover
        subject.desc = desc
        if models.Subject.objects.exclude(pk=subject.pk).filter(name=subject.name).exists():
            return simplejson.dumps({
                'ret_code': 1000, 
                'field': 'name', 
                'error': u'应用专题名已存在' 
            })
        models.edit_subject(subject, apps, request.user)

    return _ok_json


@dajaxice_register(method='POST')
@check_login
def delete_subject(request, id):
    models.Subject.objects.get(pk=id).delete(pk=id)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def drop_subject(request, id):
    models.drop_subject(id, request.user)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def sort_subjects(request, subjects):
    pks = [int(s.pk) for s in subjects.split(",")]
    models.sort_subjects(pks)
    return _ok_json


@dajaxice_register(method='POST')
def get_apps(request, pks):
    pks = [int(pk) for pk in pks.split(",")]
    apps = models.App.objects.filter(pk__in=pks)
    results = [{'id': app.pk, 'text': app.name} for app in apps]
    return simplejson.dumps({'results': results})
