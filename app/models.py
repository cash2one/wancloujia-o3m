# coding: utf-8
from django.db import models

# Create your models here.
class App(models.Model):
    #serial-number ?
    #version ?
    #category ?
    name = models.CharField(verbose_name=u'名称', max_length=20)
    promotion = models.BooleanField(verbose_name=u'是否推广')
    create_date = models.DateField(verbose_name=u'创建时间')
    status = models.BooleanField(verbose_name=u'是否上线')

class Subject(models.Model):
    #position ?
    #creator ?
    name = models.CharField(verbose_name=u'名称', max_length=20)
    cover = models.ImageField(verbose_name=u'图片', upload_to='ad/%Y/%m/%d', max_length=50)
    upload_date = models.DateField(verbose_name=u'上传时间')
    desc = models.CharField(verbose_name=u'描述', max_length=200)

class AppGroup(models.Model):
    app = models.ForeignKey(App, verbose_name=u'应用')
    subject = models.ForeignKey(Subject, verbose_name=u'专题')

'''
class Feedback(models.Model):
    #brand?
    brand = models.CharField(verbose_name='品牌')
    #model_number?
    model_number = models.CharField(verbose_name='产品型号')
'''

