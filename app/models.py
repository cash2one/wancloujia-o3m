# coding: utf-8
import logging
import os.path, random
from datetime import datetime

from taggit.managers import TaggableManager

from django.db import models, transaction, connection
from django.contrib.auth.models import User
from django.core.cache import cache
import generate_path
import urllib

logger = logging.getLogger(__name__)


class UploadApk(models.Model):
    file = models.FileField(upload_to=generate_path("apks"), max_length=1024)
    md5 = models.CharField(max_length=32, null=True)

class App(models.Model):
    PACKAGE_LENGTH_LIMIT = 100
    apk = models.ForeignKey(UploadApk)
    slogan = models.CharField(verbose_name=u'标语', max_length=30)
    name = models.CharField(verbose_name=u'应用名称', max_length=20)
    package = models.CharField(verbose_name=u'应用包名', max_length=PACKAGE_LENGTH_LIMIT)
    app_icon = models.CharField(verbose_name=u'应用图标', max_length=255, help_text=u'图标大小限制10k以下，尺寸为72*72px')
    version = models.CharField(verbose_name=u'版本号', max_length=255)
    sdk_version = models.CharField(verbose_name=u'系统最低版本', max_length=255, default="", blank=True)
    version_code = models.IntegerField(verbose_name=u'版本代码')
    create_date = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)
    update_date = models.DateTimeField(verbose_name=u'更新时间', auto_now=True)
    desc = models.CharField(verbose_name=u'编辑点评', max_length=255)
    longDesc = models.TextField(verbose_name=u'应用描述', max_length=1000)
    permissions = models.TextField(verbose_name=u'应用权限列表', default="", blank=True)
    download_num = models.IntegerField(verbose_name=u'下载数目')
    comment_num = models.IntegerField(verbose_name=u'评价数目')
    like_num = models.IntegerField(verbose_name=u'喜欢数目')

    screen1 = models.CharField(verbose_name=u'应用截图1', max_length=255, help_text=u'限制100k以下，尺寸为160*265px')
    screen2 = models.CharField(verbose_name=u'应用截图2', null=True, max_length=255, help_text=u'图片大小限制160*265px')
    screen3 = models.CharField(verbose_name=u'应用截图3', null=True, max_length=255, help_text=u'图片大小限制160*265px')
    screen4 = models.CharField(verbose_name=u'应用截图4', null=True, max_length=255, help_text=u'图片大小限制160*265px')
    screen5 = models.CharField(verbose_name=u'应用截图5', null=True, max_length=255, help_text=u'图片大小限制160*265px')
    screen6 = models.CharField(verbose_name=u'应用截图6', null=True, max_length=255, help_text=u'图片大小限制160*265px')
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

    def save(self, *args, **kwargs):
        if self.download_num is None:
            random.seed()
            self.download_num = random.randrange(1000000, 2000000)
        if self.like_num is None:
            random.seed()
            self.like_num = random.randrange(1000, 20000)
        if self.comment_num is None:
            random.seed()
            self.comment_num = random.randrange(1000, 20000)
        try:
            if self.app_icon:
                convert_img(self.app_icon,'icon')
            if self.screen1:
                convert_img(self.screen1,'app_img')
            if self.screen2:
                convert_img(self.screen2,'app_img')
            if self.screen3:
                convert_img(self.screen3,'app_img')
            if self.screen4:
                convert_img(self.screen4,'app_img')
            if self.screen5:
                convert_img(self.screen5,'app_img')
            if self.screen6:
                convert_img(self.screen6,'app_img')
            print 'success'
        except:
            logger.debug('covert fail')
            print 'fail'
        super(App, self).save(*args, **kwargs)


_MAX_SUBJECTS = 1024 * 1024


class Subject(models.Model):
    name = models.CharField(verbose_name=u'名称', max_length=20, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.name

    def available(self):
        return True

    def apps(self):
        return map(lambda item: item.app, AppGroup.objects.filter(subject=self).order_by('position'))

    def appPks(self):
        arr = []
        for app in self.apps():
            arr = arr + [str(app.pk), app.name]

        return ",".join(arr)

class Plate(models.Model):
    position = models.CharField(verbose_name=u'位置', max_length=20, unique=True)
    name = models.CharField(verbose_name=u'名称', max_length=20, unique=True)
    cover = models.CharField(verbose_name=u'图片', max_length=1024)

    def __unicode__(self):
        return self.name

    def apps(self):
        return map(lambda item: item.app, AppGroupPlate.objects.filter(plate=self).order_by('position'))

    def appPks(self):
        arr = []
        for app in self.apps():
            arr = arr + [str(app.pk), app.name]

        return ",".join(arr)

    def save(self, *args, **kwargs):
        try:
            if self.position.find('top') != -1:
                convert_img(self.cover, 'plate_top')
            elif self.position.find('middle') != -1:
                convert_img(self.cover, 'plate_middle')
            elif self.position.find('bottom') != -1:
                convert_img(self.cover, 'plate_bottom')
            else: 
                logger.debug('plate wrong type')
        except:
            logger.debug('plate convert fail')

        super(Plate, self).save(*args, **kwargs)

class AppGroup(models.Model):
    app = models.ForeignKey(App, verbose_name=u'应用')
    subject = models.ForeignKey(Subject, verbose_name=u'专题')
    position = models.IntegerField(editable=False)

class AppGroupPlate(models.Model):
    app = models.ForeignKey(App, verbose_name=u'应用')
    plate = models.ForeignKey(Plate, verbose_name=u'集合页')
    position = models.IntegerField(editable=False)


def _publish_subject(pk):
    count = len(Subject.objects.filter(online=True))
    subject =Subject.objects.get(pk=pk)
    subject.position = count + 1
    subject.online = True
    subject.save()


def _set_included_apps(subject, apps):
    AppGroup.objects.filter(subject=subject).delete()
    print apps
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

@transaction.commit_manually
def edit_plate(plate, apps):
    try:
        AppGroupPlate.objects.filter(plate=plate).delete()
        for i in range(0, len(apps)):
            app = App.objects.get(pk=apps[i])
            AppGroupPlate(plate=plate, app=app, position=i+1).save()
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

def convert_img(img, type):
    img_path = urllib.unquote(str(img))
    if type == 'icon':
        os.system("convert -resize 70x70 -strip -quality 80% " + '/data/og.proj' + img_path + ' /data/og.proj' + img_path)
        logger.debug('icon success')
    elif type == 'app_img':
        os.system("convert -resize 160x265 -strip -quality 80% " + '/data/og.proj' + img_path + ' /data/og.proj' + img_path)
        logger.debug('app_img success')
    elif type == 'plate_top':
        os.system("convert -resize 300x200 -strip -quality 80% " + '/data/og.proj' + img_path + ' /data/og.proj' + img_path)
        logger.debug('top success')
    elif type == 'plate_middle':
        os.system("convert -resize 724x166 -strip -quality 80% " + '/data/og.proj' + img_path + ' /data/og.proj' + img_path)
        logger.debug('middle success')
    elif type == 'plate_bottom':
        os.system("convert -resize 219x210 -strip -quality 80% " + '/data/og.proj' + img_path + ' /data/og.proj' + img_path)
        logger.debug('bottom success')
    else:
        logger.debug('wrong type')
