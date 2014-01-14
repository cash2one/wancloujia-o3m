#coding: utf-8

from django.db import models

# Create your models here.
class BrandModel(models.Model):
    BRAND_LENGTH_LIMIT = 32
    brand = models.CharField(verbose_name=u'pinpai', max_length=BRAND_LENGTH_LIMIT)
    model = models.CharField(verbose_name=u'jixing', max_length=16)


class DID(models.Model):
    did = models.CharField(verbose_name=u'imei', max_length= 32)