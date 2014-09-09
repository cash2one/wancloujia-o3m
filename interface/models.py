# coding: utf-8
from django.db import models, connection
from django.db.models.query import QuerySet

from mgr.models import Company, Store, Employee
from app.models import App

class LogEntity(models.Model):
    content = models.CharField(max_length=10240, default='')
    create = models.DateTimeField()

    class Meta:
        ordering = ('create',)


class LogQuerySet(QuerySet):
    def filter_by_organization(self, organization):
        emps = Employee.objects.filter_by_organization(organization)
        pks = emps.values_list('pk', flat=True)
        return self.filter(uid__in=pks)


class LogManager(models.Manager):
    def get_query_set(self):
        return LogQuerySet(self.model)

    def filter_by_organization(self, organization):
        return self.get_query_set().filter_by_organization(organization)


class LogMeta(models.Model):
    u"""
    装机数据查询的日志元数据
    """

    BRAND_LENGTH_LIMIT = 32
    date = models.DateField(db_index=True, editable=False)
    uid = models.IntegerField(db_index=True, editable=False)
    did = models.CharField(verbose_name=u'chuanhao', max_length=16, editable=False)
    brand = models.CharField(verbose_name=u'pinpai', max_length=BRAND_LENGTH_LIMIT, editable=False)
    model = models.CharField(verbose_name=u'jixing', max_length=16, editable=False)
    appID = models.CharField(max_length=16, editable=False)
    appPkg = models.CharField(max_length=App.PACKAGE_LENGTH_LIMIT, editable=False)

    objects = LogManager()

    class Meta:
        permissions=(
            ('view_organization_statistics', "Can view organization's statistics"),
        )


class InstalledAppLogEntity(models.Model):
    u"""
    应用安装统计日志分析结果项
    """
    """
    keys
    """
    date = models.DateField(db_index=True, editable=False)
    region = models.IntegerField(db_index=True, null=True)
    company = models.IntegerField(db_index=True, null=True)
    store = models.IntegerField(db_index=True, null=True)
    uid = models.IntegerField(db_index=True, editable=False)
    appName = models.CharField(max_length=24)
    popularize = models.BooleanField(editable=False)
    appID = models.CharField(db_index=True, max_length=16, editable=False)
    appPkg = models.CharField(max_length=32)
    """
    values
    """
    installedTimes = models.IntegerField(editable=False)

    objects = LogManager()


class UserDeviceLogEntity(models.Model):
    u"""
    手机安装统计
    """

    """
    keys
    """
    date = models.DateField(db_index=True, editable=False)
    region = models.IntegerField(db_index=True, null=True)
    company = models.IntegerField(db_index=True, null=True)
    store = models.IntegerField(db_index=True, null=True)
    uid = models.IntegerField(db_index=True)
    appPkg = models.CharField(max_length=App.PACKAGE_LENGTH_LIMIT, editable=False)
    """
    values
    """
    deviceCount = models.IntegerField()
    popularizeAppCount = models.IntegerField()
    appCount = models.IntegerField()


class DeviceLogEntity(models.Model):
    u"""
    机型统计
    """
    """
    keys
    """
    date = models.DateField(db_index=True, editable=False)
    region = models.IntegerField(db_index=True, null=True)
    company = models.IntegerField(db_index=True, null=True)
    store = models.IntegerField(db_index=True, null=True)
    uid = models.IntegerField(db_index=True)
    did = models.CharField(max_length=255, editable=False)
    brand = models.CharField(max_length=255)

    appPkg = models.CharField(max_length=App.PACKAGE_LENGTH_LIMIT, editable=False)
    appID = models.CharField(max_length=16, editable=False)
    appName = models.CharField(max_length=24)

    """
    values
    """
    model = models.CharField(max_length=32)
    popularizeAppCount = models.IntegerField()
    appCount = models.IntegerField()

class DownloadLogEntity(models.Model):
    u"""
    下载统计
    """
    datetime = models.DateTimeField(db_index=True, editable=False)
    ip = models.CharField(max_length=20)
    appPkg = models.CharField(max_length=App.PACKAGE_LENGTH_LIMIT, editable=False)
    appId = models.CharField(max_length=16, editable=False)
    appName = models.CharField(max_length=24, editable=False)
    module = models.CharField(max_length=30, editable=False, default="")
    srcPage = models.CharField(max_length=30, editable=False)

    class Meta:
        app_label = "interface"

class AdsLogEntity(models.Model):
    u"""
    广告统计
    """
    datetime = models.DateTimeField(db_index=True)
    ip = models.CharField(max_length=20)
    adTitle = models.CharField(max_length=20)
    op = models.CharField(max_length=10)

    class Meta:
        app_label = "interface"

class AdsStaEntity(models.Model):
    """
    新的广告统计---以前的统计量大了撑不住！
    """
    datetime = models.DateField(db_index=True)
    view = models.IntegerField(default=0)
    main_click = models.IntegerField(default=0)
    side_click = models.IntegerField(default=0)

    class Meta:
        app_label = "interface"

class PlateStaEntity(models.Model):
    u"""
    模板统计
    """
    datetime = models.DateField(db_index=True)
    view = models.IntegerField(default=0)
    click = models.IntegerField(default=0)
    top1 = models.IntegerField(default=0)
    top2 = models.IntegerField(default=0)
    top3 = models.IntegerField(default=0)
    top4 = models.IntegerField(default=0)
    top5 = models.IntegerField(default=0)
    top6 = models.IntegerField(default=0)
    top7 = models.IntegerField(default=0)
    top8 = models.IntegerField(default=0)
    top9 = models.IntegerField(default=0)
    middle = models.IntegerField(default=0)
    bottom1 = models.IntegerField(default=0)
    bottom2 = models.IntegerField(default=0)
    bottom3 = models.IntegerField(default=0)

    class Meta:
        app_label = "interface"
