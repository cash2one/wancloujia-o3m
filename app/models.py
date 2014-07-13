# coding: utf-8
import logging
import os.path
from datetime import datetime

from taggit.managers import TaggableManager

from django.db import models, transaction, connection
from django.contrib.auth.models import User
from django.core.cache import cache
import generate_path

logger = logging.getLogger(__name__)


class UploadApk(models.Model):
    file = models.FileField(upload_to='apks/%Y/%m/%d', max_length=1024)
    md5 = models.CharField(max_length=32, null=True)

class App(models.Model):
    PACKAGE_LENGTH_LIMIT = 100
    apk = models.ForeignKey(UploadApk)
    slogan = models.CharField(verbose_name=u'标语', max_length=30)
    name = models.CharField(verbose_name=u'应用名称', max_length=20)
    package = models.CharField(verbose_name=u'应用包名', max_length=PACKAGE_LENGTH_LIMIT, unique=True)
    app_icon = models.CharField(verbose_name=u'应用图标', max_length=255)
    version = models.CharField(verbose_name=u'版本号', max_length=255)
    sdk_version = models.CharField(verbose_name=u'系统最低版本', max_length=255)
    version_code = models.IntegerField(verbose_name=u'版本代码')
    create_date = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    update_date = models.DateTimeField(verbose_name=u'更新时间', auto_now=True)
    desc = models.CharField(verbose_name=u'编辑点评', max_length=255)
    longDesc = models.TextField(verbose_name=u'应用描述')
    permissions = models.TextField(verbose_name=u'应用权限列表')

    screen1 = models.CharField(verbose_name=u'应用截图1', max_length=255)
    screen2 = models.CharField(verbose_name=u'应用截图2', null=True, max_length=255)
    screen3 = models.CharField(verbose_name=u'应用截图3', null=True, max_length=255)
    screen4 = models.CharField(verbose_name=u'应用截图4', null=True, max_length=255)
    screen5 = models.CharField(verbose_name=u'应用截图5', null=True, max_length=255)
    screen6 = models.CharField(verbose_name=u'应用截图6', null=True, max_length=255)
    tags = TaggableManager()

    def available(self):
        return True

    def size(self):
        val = cache.get(self.package, -1)
        cache.close()
        if val == -1:
            val = os.path.getsize(self.apk.file.path)
            cache.set(self.package, val, 30)
        return val

    def __unicode__(self):
        return self.name


_MAX_SUBJECTS = 1024 * 1024


class Subject(models.Model):
    name = models.CharField(verbose_name=u'名称', max_length=20, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.name

    def available(self):
        return True

    def apps(self):
        return map(lambda item: item.app, AppGroup.objects.filter(subject=self))

    def appPks(self):
        arr = []
        for app in self.apps():
            arr = arr + [str(app.pk), app.name]

        return ",".join(arr)


class AppGroup(models.Model):
    app = models.ForeignKey(App, verbose_name=u'应用')
    subject = models.ForeignKey(Subject, verbose_name=u'专题')
    position = models.IntegerField(editable=False)


def _publish_subject(pk):
    count = len(Subject.objects.filter(online=True))
    subject =Subject.objects.get(pk=pk)
    subject.position = count + 1
    subject.online = True
    subject.save()


def _set_included_apps(subject, apps):
    AppGroup.objects.filter(subject=subject).delete()
    for i in range(0, len(apps)):
        app = App.objects.get(pk=apps[i])
        AppGroup(subject=subject, app=app, position=i+1).save()


@transaction.commit_manually
def add_subject(subject, apps, user):
    try:
        subject.creator = user
        subject.create_date = datetime.now()
        subject.updator = user
        subject.update_date = datetime.now()
        subject.save()
        _set_included_apps(subject, apps) 
        _publish_subject(subject.pk)
    except Exception as e:
        transaction.rollback()
        logger.exception(e)
        raise e
    else:
        transaction.commit()


@transaction.commit_manually
def edit_subject(subject, apps, user):
    try:
        subject.updator = user
        subject.update_date = datetime.now();
        subject.save()
        _set_included_apps(subject, apps) 
    except Exception as e:
        transaction.rollback()
        logger.exception(e)
        raise e
    else:
        transaction.commit()


def _drop_subject(id):
    subject = Subject.objects.get(pk=id)
    c = connection.cursor()
    try:
        sql= '''update app_subject set position = position - 1
                 where position > %d and online = 1 ''' % subject.position
        c.execute(sql)
    finally:
        c.close()
    subject.position = _MAX_SUBJECTS
    subject.online = False
    subject.save()

@transaction.commit_manually
def drop_subject(id):
    try:
        _drop_subject(id)    
    except Exception as e:
        transaction.rollback()
        logger.exception(e)
        raise e
    else:
        transaction.commit()


@transaction.commit_manually
def publish_subject(id):
    try: 
        _publish_subject(id)
    except Exception as e:
        logger.exception(e)
        transaction.rollback()
        raise e
    else:
        transaction.commit()


@transaction.commit_manually
def sort_subjects(pks):
    try: 
        Subject.objects.exclude(pk__in=pks).update(position=_MAX_SUBJECTS, online=False)
        Subject.objects.filter(pk__in=pks).update(online=True)
        for i in range(0, len(pks)):
            subject = Subject.objects.get(pk=pks[i])
            subject.position = i + 1
            subject.save()
    except Exception as e:
        logger.exception(e)
        transaction.rollback()
        raise e
    else:
        transaction.commit()


@transaction.commit_manually
def delete_subject(pk):
    try: 
        _drop_subject(pk)
        Subject.objects.get(pk=pk).delete()
    except Exception as e:
        logger.exception(e)
        transaction.rollback()
        raise e
    else:
        transaction.commit()
