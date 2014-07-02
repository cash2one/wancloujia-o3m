# coding: utf-8
from dajaxice.decorators import dajaxice_register
import feedback.models
from og.decorators import *

logger = logging.getLogger(__name__)

_invalid_data_msg = u'数据出错，请检查'
_invalid_data_json = simplejson.dumps({'ret_code': 1000, 'ret_msg': _invalid_data_msg})
_ok_json = simplejson.dumps({'ret_code': 0})

@dajaxice_register(method='POST')
@check_login
def handle_feedback(request, id):
    feedback.models.handle_feedback(id)
    return _ok_json


@dajaxice_register(method='POST')
@check_login
def delete_feedback(request, id):
    feedback.models.delete_feedback(id)
    return _ok_json