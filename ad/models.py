# coding: utf-8
from datetime import datetime
import logging

from django.db import models, connection, transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

class AD(models.Model):
    title = models.CharField(verbose_name=u'广告标题', max_length=50)
    cover = models.CharField(verbose_name=u'广告图片', max_length=100)
    desc = models.CharField(verbose_name=u'广告介绍', max_length=50, blank=True)
    from_date = models.DateTimeField(verbose_name=u'上线时间')
    to_date = models.DateTimeField(verbose_name=u'下线时间')
    visible = models.BooleanField(verbose_name=u'广告状态')
    approved = models.BooleanField(verbose_name=u'审核状态')
    position = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title

    def available(self):
        return self.visible

    def in_period(self):
        return self.from_date <= timezone.now() <= self.to_date

    class Meta:
        permissions = (
            ('sort_ad', 'Can sort the advertisements'),
        )


_MAX_ADS = 1024

@transaction.commit_manually
def sort_ad(pks):
    try:
        AD.objects.exclude(pk__in=pks).update(position=_MAX_ADS, visible=False)
        AD.objects.filter(pk__in=pks).update(visible=True)
        for i in range(0, len(pks)):
            ad = AD.objects.get(pk=pks[i])
            ad.position = i + 1
            ad.save()
    except Exception as e:
        logger.exception(e)
        transaction.roll_back()
        raise e
    else:
        transaction.commit()


def _set_ad_visible(pk):
    count = len(AD.objects.filter(visible=True))
    ad = AD.objects.get(pk=pk)
    ad.position = count
    ad.save()


def _set_ad_invisible(pk):
    ad = AD.objects.get(pk=pk)
    c = connection.cursor()
    try:
        c.execute("update ad_ad set position = position - 1 where position > %d and visible = 1" % ad.position)
    finally:
        c.close()
    ad.position = _MAX_ADS
    ad.visible = False
    ad.save()


@transaction.commit_manually
def add_ad(ad):
    try: 
        ad.save()
        if ad.visible:
            _set_ad_visible(ad.pk)
        else:
            ad.position = _MAX_ADS
            ad.save()
    except Exception as e:
        logger.exception(e)
        transaction.roll_back()
        raise e
    else:
        transaction.commit()


@transaction.commit_manually
def edit_ad(ad):
    visible = ad.visible
    visible_changed = AD.objects.get(pk=ad.pk).visible != ad.visible
    try:
        ad.save()
        if visible_changed:
            if visible:
                _set_ad_visible(ad.pk)
            else:
                _set_ad_invisible(ad.pk)
    except Exception as e:
        logger.exception(e)
        transaction.roll_back()
        raise e
    else:
        transaction.commit()


@transaction.commit_manually
def delete_ad(pk): 
    try:
        ad = AD.objects.get(pk=pk)
        if not ad.visible:
            ad.delete()
        else:
            _set_ad_invisible(pk)
            delete_ad(pk)
    except Exception as e:
        logger.exception(e)
        transaction.roll_back()
        raise e
    else:
        transaction.commit()
    
