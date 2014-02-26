#coding: utf-8
import logging
from functools import wraps

from django.utils import simplejson
from dajaxice.utils import deserialize_form

logger = logging.getLogger(__name__)

def preprocess_form(func):
    @wraps(func)
    def wrap(request, *args, **kwargs):
        f = kwargs["form"]
        form = deserialize_form(f)
        dict = map(lambda k: (k, form[k]), form)
        logger.debug("form: " + str(dict))

        return func(request, form=form)
    return wrap

