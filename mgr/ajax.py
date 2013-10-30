# coding: utf-8
import logging
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form
from framework.decorators import request_delay
from forms import ModifyPasswordForm

logger = logging.getLogger(__name__)

@dajaxice_register(method='POST')
#@request_delay(3)
def modify_password(request, form):
    form = deserialize_form(form)
    dict = map(lambda k: (k, form[k]), form)
    logger.debug("form: " + str(dict))

    f = ModifyPasswordForm(form)
    if not f.is_valid():
        logger.debug('modify_password: form is invalid')
        ret_msg = u'数据出错，请检查'
        return simplejson.dumps({'ret_code': 1000, 'ret_msg': ret_msg})

    user = request.user
    origin = f.cleaned_data["origin"]
    if not user.check_password(origin):
        logger.debug("password not match, param: %s", origin)
        ret_msg = u'密码不正确，请重新填写'
        return simplejson.dumps({'ret_code': 1000, 'ret_msg': ret_msg})

    password = f.cleaned_data["password"]
    user.set_password(password)
    user.save()
    return simplejson.dumps({'ret_code': 0})

