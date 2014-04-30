# coding: utf-8
from django.db import models, connection
from django.db.models.query import QuerySet

from mgr.models import Company, Store, Employee
from app.models import App

class LogEntity(models.Model):
    content = models.CharField(max_length=10240, default='')
    create = models.DateTimeField()

    class Meta:
        permissions=(
            ('view_all_data', "Can view alldata"),
        )


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
    imei = models.CharField(verbose_name=u'IMEI', max_length=64, editable=False, null=True)
    model = models.CharField(verbose_name=u'jixing', max_length=16, editable=False)
    subject = models.IntegerField(verbose_name=u'zhuti', editable=False)
    client_version = models.CharField(max_length=20)
    installed = models.BooleanField(editable=False)
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

