#coding: utf-8

from django.db import models
from modelmgr.models import Model

class BrandModel(models.Model):
    BRAND_LENGTH_LIMIT = 32
    brand = models.CharField(verbose_name=u'pinpai', max_length=BRAND_LENGTH_LIMIT)
    model = models.CharField(verbose_name=u'jixing', max_length=16)
	
    def __unicode__(self):
        return self.model

class DID(models.Model):
    did = models.CharField(verbose_name=u'imei', max_length= 32)


def query_model_name(ua):
    models = Model.objects.filter(ua=ua)
    return ua if len(models) == 0 else models[0].name
