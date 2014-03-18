# coding: utf-8
from django.db import models

class Model(models.Model):
    name = models.CharField(verbose_name=u'机型名称', max_length=100, unique=True)
    ua = models.CharField(verbose_name=u'机型代码', max_length=100, unique=True)

    def __unicode__(self):
        return self.name
