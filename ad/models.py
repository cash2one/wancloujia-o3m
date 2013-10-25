# coding: utf-8
from django.db import models

# Create your models here.

class AD(models.Model):
    title = models.CharField(verbose_name='标题', max_length='50')
    cover = models.ImageField(verbose_name='图片', upload_to='ad/%Y/%m/%d')
    #status?
    online_date = models.DateField(verbose_name='上线时间', auto_now_add=True)
    offline_date = models.DateField(verbose_name='下线时间')
    visible = models.BooleanField(verbose_name='显示状态')
    approved = models.BooleanField(verbose_name='审核状态')

    def __unicode__(self):
        return self.title


