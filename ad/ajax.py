# coding: utf-8
import logging

from django.utils import simplejson
from django.contrib.auth.models import User
from dajaxice.decorators import dajaxice_register

from forms import *
from models import *
from suning.decorators import *

logger = logging.getLogger(__name__)

_invalid_data_msg = u'数据出错，请检查'
_invalid_data_json = simplejson.dumps({'ret_code': 1000, 'ret_msg': _invalid_data_msg})
_ok_json = simplejson.dumps({'ret_code': 0})


@dajaxice_register(method='POST')
@check_login
def delete_ad(request, id):
    AD.objects.get(pk=id).delete()
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def add_edit_ad(request, form, visible):
    form = deserialize_form(form)
    f = ADForm(form)
    if not f.is_valid():
        logger.warn("%s: form is invalid" % __name__)
        logger.warn(f.errors)
        return _invalid_data_json

    ad = f.save(commit=False)
    ad.visible = visible
    if form["id"] == "":
        if AD.objects.filter(title=ad.title).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'title', 'error': u'广告标题已存在'})
        ad.save()
        return _ok_json
    else:
        ad.pk = form["id"]
        if AD.objects.exclude(pk=ad.pk).filter(title=ad.title).exists():
            return simplejson.dumps({'ret_code': 1000, 'field': 'title', 'error': u'广告标题已存在'})
        ad.save()
        return _ok_json

