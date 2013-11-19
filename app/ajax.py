# coding: utf-8
import logging
from datetime import datetime

from django.utils import simplejson
from django.contrib.auth.models import User
from dajaxice.decorators import dajaxice_register

from models import *
from forms import *
from suning.decorators import *

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

    app = f.save(commit=False)
    app.name = form["name"]
    app.package = form["package"]
    app.app_icon = form["app_icon"]
    if form["id"] == "":
        if App.objects.filter(package=app.package).exists():
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'应用已存在'})
        app.online = True
        app.save()
    else:
        app.pk = form["id"]
        if App.objects.get(pk=app.pk).package != app.package:
            return simplejson.dumps({'ret_code': 1000, 'ret_msg': u'应用包名不相同'})
        app_stored = App.objects.get(pk=app.pk)
        app.create_date = app_stored.create_date
        app.online = app_stored.online
        app.save()

    return _ok_json


@dajaxice_register(method='POST')
@check_login
def delete_app(request, id):
    App.objects.get(pk=id).delete()
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def publish_app(request, id):
    App.objects.filter(pk=id).update(online=True)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def drop_app(request, id):
    App.objects.filter(pk=id).update(online=False)
    return _ok_json
