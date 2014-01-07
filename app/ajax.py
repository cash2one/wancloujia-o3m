# coding: utf-8
import logging
import time
from datetime import datetime

from django.db import transaction, connection
from django.utils import simplejson
from django.contrib.auth.models import User
from dajaxice.decorators import dajaxice_register

from suning.decorators import request_delay, oplogtrack
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
        __add_app(app, request.user.username)
    else:
        app.pk = form["id"]
        if models.App.objects.get(pk=app.pk).package != app.package:
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'应用包名不相同'})
        __edit_app(app, request.user.username)

    return _ok_json


@dajaxice_register(method='POST')
@check_login
def delete_app(request, id):
    model = models.App.objects.get(pk=id)
    __remove_app(model, request.user.username)
    return _ok_json


@transaction.commit_manually
def _drop_app(id):
    try:
        models.App.objects.filter(pk=id).update(online=False)
        models.AppGroup.objects.filter(app__pk=id).delete()
    except Exception as e:
        transaction.rollback()
        logger.exception(e)
        raise e
    else:
        transaction.commit()


@dajaxice_register(method='POST')
@check_login
def publish_app(request, id):
    #models.App.objects.filter(pk=id).update(online=True)
    model = models.App.objects.get(pk=id)
    __pub_app(model, request.user.username)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def drop_app(request, id):
    model = models.App.objects.get(pk=id)
    __drop_app(model, request.user.username)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
@preprocess_form
def add_edit_subject(request, form):
    pk = form["id"]
    name = form["name"]
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
        __add_subj(subject, request.user.username)
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
        __edit_subj(subject, request.user.username)

    return _ok_json


@dajaxice_register(method='POST')
@check_login
def delete_subject(request, id):
    model = models.Subject.objects.get(pk=id)
    __remove_subj(model, request.user.username)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def drop_subject(request, id):
    model = models.Subject.objects.get(pk=id)
    __drop_subj(model, request.user.username)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def publish_subject(request, id):
    model = models.Subject.objects.get(pk=id)
    __pub_subj(model, request.user.username)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def sort_subjects(request, pks):
    pks = [int(pk) for pk in pks.split(",")]
    __sort_subj(request.user.username, pks)
    return _ok_json


@dajaxice_register(method='POST')
#@request_delay(3)
def get_apps(request, subject, pks):
    pks = [int(pk) for pk in pks.split(",")]
    groups = models.AppGroup.objects.filter(subject__pk=subject).filter(app__pk__in=pks).filter(app__online=True).order_by("position")
    results = [{'id': g.app.pk, 'text': g.app.name} for g in groups]
    logger.debug(results)
    return simplejson.dumps({'results': results})


def __add_app(model, username):
    model.online = True
    model.save()
    oplogtrack(u'新增应用', username, model)

def __edit_app(model, username):
    app_stored = App.objects.get(pk=model.pk)
    model.create_date = app_stored.create_date
    model.online = app_stored.online
    model.save()
    oplogtrack(u'编辑应用', username, model)

def __remove_app(model, username):
    model.delete()
    oplogtrack(u'删除应用', username, model)

def __pub_app(model, username):
    model.online = True
    model.save()
    oplogtrack(u'上线应用', username, model)

def __drop_app(model, username):
    _drop_app(model.pk)
    oplogtrack(u'下线应用', username, model)

def __add_subj(model, username):
    oplogtrack(u'新增应用专题', username, model)

def __edit_subj(model, username):
    oplogtrack(u'编辑应用专题', username, model)

def __remove_subj(model, username):
    models.delete_subject(model.pk)
    oplogtrack(u'删除应用专题', username, model)

def __sort_subj(username, pks):
    models.sort_subjects(pks)
    oplogtrack(u'调整应用专题顺序', username)

def __pub_subj(model, username):
    models.publish_subject(model.pk)
    oplogtrack(u'上线应用专题', username)

def __drop_subj(model, username):
    models.drop_subject(model.pk)
    oplogtrack(u'下线应用专题', username)