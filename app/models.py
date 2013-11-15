# coding: utf-8
import os.path

from django.db import models


class UploadApk(models.Model):
    file = models.FileField(upload_to='apks/%Y/%m/%d')


class Category(models.Model):
    parent = models.ForeignKey("self", verbose_name=u'所属类型', null=True)
    name = models.CharField(verbose_name=u'名称', unique=True, max_length=20)

    def __unicode__(self):
        return self.name


class App(models.Model):
    apk = models.ForeignKey(UploadApk)
    name = models.CharField(verbose_name=u'应用名称', max_length=20)
    package = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, verbose_name=u'应用类型')
    app_icon = models.CharField(verbose_name=u'应用图标', max_length=100)
    version = models.CharField(verbose_name=u'版本号', max_length=20)
    popularize = models.BooleanField(verbose_name=u'是否推广')
    create_date = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    online = models.BooleanField(verbose_name=u'是否上线')
    desc = models.CharField(verbose_name=u'应用描述', max_length=400)

    def size(self): 
        return os.path.getsize(self.apk.file.path)

    class Meta:
        permissions = (
            ('publish_app', 'Can publish app'),
            ('drop_app', 'Can drop app'),
            ('audit_app', 'Can audit app')
        )


class Subject(models.Model):
    #position ?
    #creator ?
    name = models.CharField(verbose_name=u'名称', max_length=20)
    cover = models.ImageField(verbose_name=u'图片', upload_to='ad/%Y/%m/%d', max_length=50)
    upload_date = models.DateField(verbose_name=u'上传时间')
    desc = models.CharField(verbose_name=u'描述', max_length=200)

    def __unicode__(self):
        return self.name


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
