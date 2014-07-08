# coding: utf-8
import logging
import os.path
from datetime import datetime

from django.db import models, transaction, connection
from django.contrib.auth.models import User

from modelmgr.models import Model

logger = logging.getLogger(__name__)


class UploadApk(models.Model):
    file = models.FileField(upload_to='apks/%Y/%m/%d')
    md5 = models.CharField(max_length=32, null=True)
    size = models.IntegerField(default=0)


class Category(models.Model):
    parent = models.ForeignKey("self", verbose_name=u'所属类型', null=True)
    name = models.CharField(verbose_name=u'名称', unique=True, max_length=20)

    def __unicode__(self):
        return self.name


class App(models.Model):
    PACKAGE_LENGTH_LIMIT = 100
    apk = models.ForeignKey(UploadApk)
    name = models.CharField(verbose_name=u'应用名称', max_length=20)
    package = models.CharField(max_length=PACKAGE_LENGTH_LIMIT)
    category = models.ForeignKey(Category, verbose_name=u'应用类型', null=True, blank=True)
    app_icon = models.CharField(verbose_name=u'应用图标', max_length=100)
    version = models.CharField(verbose_name=u'版本号', max_length=255)
    version_code = models.IntegerField(verbose_name=u'版本代码')
    popularize = models.BooleanField(verbose_name=u'是否推广')
    open_after_install = models.BooleanField(verbose_name=u'安装后是否打开')
    create_date = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    online = models.BooleanField(verbose_name=u'是否上线')
    desc = models.CharField(verbose_name=u'应用描述', max_length=50, null=True)

    def available(self):
        return self.online

    def size(self):
        #import interface.storage
        #dfs = interface.storage.hdfs_storage()
        #return dfs.size(self.apk.file.path)
        return os.path.getsize(self.apk.file.path)

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
    cover = models.CharField(verbose_name=u'图片', max_length=100)
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
        verbose_name = u'应用专题'
        verbose_name_plural = u'应用专题'



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
        if not subject.cover or len(subject.cover) == 0:
            subject.cover = "/static/img/normalsubj.png"
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

class SubjectMap(models.Model):
    TYPE_MODEL = 1
    TYPE_MEM_SIZE = 2
    TYPE_CHOICES = (
        (TYPE_MODEL, u'机型适配'),
        (TYPE_MEM_SIZE, u'存储空间适配')
    )
    type = models.IntegerField(verbose_name=u'适配类型', choices=TYPE_CHOICES)
    model = models.ForeignKey(Model, verbose_name=u'机型', null=True)

    MEM_SIZE_0M_64M = 1
    MEM_SIZE_64M_128M = 2
    MEM_SIZE_128M_512M = 3
    MEM_SIZE_512M_1G = 4
    MEM_SIZE_1G_2G = 5
    MEM_SIZE_2G_4G = 6
    MEM_SIZE_4G_8G = 7
    MEM_SIZE_8G_16G = 8
    MEM_SIZE_16G_ = 9
    MEM_SIZE_CHOICES = (
        (MEM_SIZE_0M_64M, u'0M - 64M'),
        (MEM_SIZE_64M_128M, u'64M - 128M'),
        (MEM_SIZE_128M_512M, u'128M - 512M'),
        (MEM_SIZE_512M_1G, u'512M - 1G'),
        (MEM_SIZE_1G_2G, u'1G - 2G'),
        (MEM_SIZE_2G_4G, u'2G - 4G'),
        (MEM_SIZE_4G_8G, u'4G - 8G'),
        (MEM_SIZE_8G_16G, u'8G - 16G'),
        (MEM_SIZE_16G_, u'16G以上')
    )

    mem_size = models.IntegerField(verbose_name=u'存储空间', choices=MEM_SIZE_CHOICES, blank=True, null=True)
    subject = models.ForeignKey(Subject, verbose_name=u'应用专题')
    creator = models.ForeignKey(User, verbose_name=u'创建者', related_name='subjectmap_creator')
    create_date = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    updator = models.ForeignKey(User, verbose_name=u'上次修改者', related_name='subjectmap_updator')
    update_date = models.DateTimeField(verbose_name=u'上次修改时间', auto_now=True)

    def __unicode__(self):
        t = u'机型适配' if self.type == self.TYPE_MODEL else u'存储空间适配'
        c = self.model if self.model else dict(self.MEM_SIZE_CHOICES)[self.mem_size]
        return u'%s（%s）' % (t, c)
        

    def match(self, model, bits):
        if self.type == SubjectMap.TYPE_MODEL:
            return self.model == model or model == None
        else:
            return bits == None or self.mem_size == SubjectMap.getMemSize(bits)


    @classmethod
    def getMemSize(cls, bits):
        if bits < 64 * 1000 * 1000:
            result = SubjectMap.MEM_SIZE_0M_64M
        elif bits < 128 * 1000 * 1000:
            result = SubjectMap.MEM_SIZE_64M_128M
        elif bits < 512 * 1000 * 1000:
            result = SubjectMap.MEM_SIZE_128M_512M
        elif bits < 1000 * 1000 * 1000:
            result = SubjectMap.MEM_SIZE_512M_1G
        elif bits < 2000 * 1000 * 1000:
            result = SubjectMap.MEM_SIZE_1G_2G
        elif bits < 4000 * 1000 * 1000:
            result = SubjectMap.MEM_SIZE_2G_4G
        elif bits < 8000 * 1000 * 1000:
            result = SubjectMap.MEM_SIZE_4G_8G
        elif bits < 16 * 1000 * 1000 * 1000:
            result = SubjectMap.MEM_SIZE_8G_16G
        else:
            result = SubjectMap.MEM_SIZE_16G_
        logger.debug("mem_size: %d" % result)
        return result
    

@transaction.commit_manually
def add_subjectmap(subjectmap, user):
    try:
        subjectmap.creator = user
        subjectmap.updator = user
        subjectmap.save()
    except Exception as e:
        transaction.rollback()
        logger.exception(e)
        raise e
    else:
        transaction.commit()

@transaction.commit_manually
def edit_subjectmap(subjectmap, user):
    try:
        subjectmap.updator = user
        subjectmap.save()
    except Exception as e:
        transaction.rollback()
        logger.exception(e)
        raise e
    else:
        transaction.commit()

@transaction.commit_manually
def delete_subjectmap(pk):
    try: 
        SubjectMap.objects.get(pk=pk).delete()
    except Exception as e:
        logger.exception(e)
        transaction.rollback()
        raise e
    else:
        transaction.commit()
