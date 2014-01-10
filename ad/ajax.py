# coding: utf-8
import logging

from django.utils import simplejson
from django.contrib.auth.models import User
from dajaxice.decorators import dajaxice_register

from ad import models
from forms import *
from suning.decorators import *

logger = logging.getLogger(__name__)

_invalid_data_msg = u'数据出错，请检查'
_invalid_data_json = simplejson.dumps({'ret_code': 1000, 'ret_msg': _invalid_data_msg})
_ok_json = simplejson.dumps({'ret_code': 0})


@dajaxice_register(method='POST')
@check_login
def delete_ad(request, id):
    model = models.AD.objects.get(pk=id)
    __remove(model, request.user.username, id)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def add_edit_ad(request, form, visible):
    form = deserialize_form(form)
    f = ADForm(form)
    logger.debug(f)
    if not f.is_valid():
        logger.warn("%s: form is invalid" % __name__)
        logger.warn(f.errors)
        return _invalid_data_json

    ad = f.save(commit=False)
    ad.visible = visible
    if form["id"] == "":
        if models.AD.objects.filter(title=ad.title).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'title', 'error': u'广告标题已存在'})
        __add(ad, request.user.username)
        return _ok_json
    else:
        ad.pk = form["id"]
        if models.AD.objects.exclude(pk=ad.pk).filter(title=ad.title).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'title', 'error': u'广告标题已存在'})
        __edit(ad, request.user.username)
        return _ok_json


@dajaxice_register(method='POST')
@check_login
def sort_ad(request, pks):
    __sort(pks, request.user.username)
    return _ok_json

def __add(model, username=u'未知'):
    models.add_ad(model)
    oplogtrack(0, username, model)

def __edit(model, username=u'未知'):
    models.edit_ad(model)
    oplogtrack(1, username, model)

def __remove(model=None, username=u'未知', id=-1):
    models.delete_ad(id)
    oplogtrack(2, username, model)

def __sort(pks, username=u'未知'):
    ad_pks = [int(pk) for pk in pks.split(",")]
    models.sort_ad(ad_pks)
    oplogtrack(3, username)

