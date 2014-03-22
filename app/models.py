# coding: utf-8
import logging
import os.path
from datetime import datetime

from django.db import models, transaction, connection
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class UploadApk(models.Model):
    file = models.FileField(upload_to='apks/%Y/%m/%d', max_length=1024)
    md5 = models.CharField(max_length=32, null=True)



class Category(models.Model):
    parent = models.ForeignKey("self", verbose_name=u'所属类型', null=True)
    name = models.CharField(verbose_name=u'名称', unique=True, max_length=20)

    def __unicode__(self):
        return self.name


class App(models.Model):
    PACKAGE_LENGTH_LIMIT = 100
    apk = models.ForeignKey(UploadApk)
    name = models.CharField(verbose_name=u'应用名称', max_length=20)
    package = models.CharField(max_length=PACKAGE_LENGTH_LIMIT, unique=True)
    category = models.ForeignKey(Category, verbose_name=u'应用类型')
    app_icon = models.CharField(verbose_name=u'应用图标', max_length=100)
    version = models.CharField(verbose_name=u'版本号', max_length=255)
    version_code = models.IntegerField(verbose_name=u'版本代码')
    popularize = models.BooleanField(verbose_name=u'是否推广')
    create_date = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    online = models.BooleanField(verbose_name=u'是否上线')
    desc = models.CharField(verbose_name=u'应用描述', max_length=50, null=True)
    def available(self):
        return self.online

    def size(self):
        return os.path.getsize(self.apk.file.path)
        #import interface.storage
        #dfs = interface.storage.hdfs_storage()
        #return dfs.size(self.apk.file.path)

    def __unicode__(self):
        return self.name

    class Meta:
        permissions = (
            ('publish_app', 'Can publish app'),
            ('drop_app', 'Can drop app'),
            ('audit_app', 'Can audit app')
        )


_MAX_SUBJECTS = 1024 * 1024


class Subject(models.Model):
    name = models.CharField(verbose_name=u'名称', max_length=20, unique=True)
    cover = models.CharField(verbose_name=u'图片', max_length=1024)
    desc = models.CharField(verbose_name=u'描述', max_length=200, null=True, default="")
    online = models.BooleanField(verbose_name=u'状态', default=False)

    creator = models.ForeignKey(User, verbose_name=u'创建者', related_name='creator')
    create_date = models.DateTimeField(verbose_name=u'创建时间')
    updator = models.ForeignKey(User, verbose_name=u'上次修改者', related_name='updator')
    update_date = models.DateTimeField(verbose_name=u'上次修改时间')

    position = models.IntegerField(default=_MAX_SUBJECTS)

    def __unicode__(self):
        return self.name

    def available(self):
        return self.online

    class Meta:
        permissions = (
            ('publish_subject', 'Can publish subject'),
            ('drop_subject', 'Can drop subject'),
            ('sort_subject', 'Can sort subject'),
            ('audit_subject', 'Can audit subject')
        )


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
