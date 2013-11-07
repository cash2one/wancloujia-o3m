# coding: utf-8
from django.db import models

class AD(models.Model):
    title = models.CharField(verbose_name=u'广告标题', max_length='50')
    cover = models.ImageField(verbose_name=u'广告图片', upload_to='ad/%Y/%m/%d')
    online_date = models.DateField(verbose_name=u'上线时间')
    offline_date = models.DateField(verbose_name=u'下线时间')
    visible = models.BooleanField(verbose_name=u'广告状态')
    approved = models.BooleanField(verbose_name=u'审核状态')

    def __unicode__(self):
        return self.title


