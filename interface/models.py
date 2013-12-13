# coding: utf-8
from django.db import models
from mgr.models import Company, Store, Employee
from app.models import App

class LogEntity(models.Model):
    content = models.CharField(max_length=10240, default='')
    create = models.DateTimeField()

    class Meta:
        ordering = ('create',)


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

    @classmethod
    def filter_by_organization(cls, logs, organization):
        emps = Employee.filter_by_organization(organization)
        pks = emps.values_list('pk', flat=True)
        return logs.filter(uid__in=pks)

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
    uid = models.IntegerField(db_index=True, editable=False)
    appName = models.CharField(max_length=24)
    appID = models.CharField(db_index=True, max_length=16, editable=False)
    appPkg = models.CharField(max_length=32)
    """
    values
    """
    installedTimes = models.IntegerField(editable=False)


class UserDeviceLogEntity(models.Model):
    u"""
    手机安装统计
    """

    """
    keys
    """
    date = models.DateField(db_index=True)
    uid = models.IntegerField(db_index=True)
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
    date = models.DateField(db_index=True)
    uid = models.IntegerField(db_index=True)
    brand = models.CharField(max_length=255)
    appName = models.CharField(max_length=255)
    """
    values
    """
    model = models.CharField(max_length=32)
    did = models.CharField(max_length=16)
    deviceCount = models.IntegerField()
    popularizeAppCount = models.IntegerField()
    appCount = models.IntegerField()

