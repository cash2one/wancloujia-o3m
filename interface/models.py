from django.db import models
from mgr.models import Company, Store
# Create your models here.

class LogEntity(models.Model):
    content = models.CharField(max_length=10240, default='')
    create = models.DateTimeField()

    class Meta:
        ordering = ('create',)


class LogMeta(models.Model):
    """

    """
    date = models.DateField(db_index=True, editable=False)
    uid = models.IntegerField(db_index=True, editable=False)
    did = models.CharField(verbose_name=u'chuanhao', max_length=16, editable=False)
    brand = models.CharField(verbose_name=u'pinpai', max_length=32, editable=False)
    model = models.CharField(verbose_name=u'jixing', max_length=16, editable=False)
    appID = models.CharField(max_length=16, editable=False)
    appPkg = models.CharField(max_length=32, editable=False)


class InstalledAppLogEntity(models.Model):
    """

    """
    """
    keys
    """
    date = models.DateField(db_index=True, editable=False)
    appName = models.CharField(max_length=24)
    appID = models.CharField(db_index=True, max_length=16, editable=False)
    appPkg = models.CharField(max_length=32)
    """
    values
    """
    installedTimes = models.IntegerField(editable=False)


class UserDeviceLogEntity(models.Model):
    """

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
    """

    """
    """
    keys
    """
    date = models.DateField(db_index=True)
    uid = models.IntegerField(db_index=True)
    brand = models.CharField()
    appName = models.CharField()
    """
    values
    """
    model = models.CharField(max_length=32)
    did = models.CharField(max_length=16)
    deviceCount = models.IntegerField()
    popularizeAppCount = models.IntegerField()
    appCount = models.IntegerField()

