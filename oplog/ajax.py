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
from models import *

logger = logging.getLogger(__name__)

_DEFAULT_PASSWORD= '123456'
_invalid_data_msg = u'数据出错，请检查'
_invalid_data_json = simplejson.dumps({'ret_code': 1000, 'ret_msg': _invalid_data_msg})
_ok_json = simplejson.dumps({'ret_code': 0})