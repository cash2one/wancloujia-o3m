# coding: utf-8
import logging

from django.utils import simplejson
from django.contrib.auth.models import User
from dajaxice.decorators import dajaxice_register

from modelmgr import models
from forms import *
from suning.decorators import *

logger = logging.getLogger(__name__)

_invalid_data_msg = u'数据出错，请检查'
_invalid_data_json = simplejson.dumps({'ret_code': 1000, 'ret_msg': _invalid_data_msg})
_ok_json = simplejson.dumps({'ret_code': 0})


@dajaxice_register(method='POST')
@check_login
def delete_model(request, id):
    model = models.Model.objects.get(pk=id)
    //TODO remove model
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def add_edit_model(request, form, visible):
    form = deserialize_form(form)
    f = ModelForm(form)
    logger.debug(f)
    if not f.is_valid():
        logger.warn("%s: form is invalid" % __name__)
        logger.warn(f.errors)
        return _invalid_data_json

    model = f.save(commit=False)
    if form["id"] == "":
        if models.Model.objects.filter(name=model.name).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'name', 'error': u'机型名称已存在'})
        if models.Model.objects.filter(ua=model.ua).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'ua', 'error': u'机型代码已存在'})
        //TODO add model
        return _ok_json
    else:
        model.pk = form["id"]
        if models.Model.objects.exclude(pk=model.pk).filter(name=model.name).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'name', 'error': u'机型名称已存在'})
        if models.Model.objects.exclude(pk=model.pk).filter(ua=model.ua).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'ua', 'error': u'机型代码已存在'})
            //TODO edit model
        return _ok_json
