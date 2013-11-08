# coding: utf-8
import logging

from django.db import models, connection, transaction

logger = logging.getLogger(__name__)

class AD(models.Model):
    title = models.CharField(verbose_name=u'广告标题', max_length=50)
    cover = models.CharField(verbose_name=u'广告图片', max_length=100)
    desc = models.CharField(verbose_name=u'广告介绍', max_length=400, blank=True)
    from_date = models.DateTimeField(verbose_name=u'上线时间')
    to_date = models.DateTimeField(verbose_name=u'下线时间')
    visible = models.BooleanField(verbose_name=u'广告状态')
    approved = models.BooleanField(verbose_name=u'审核状态')
    position = models.IntegerField()

    def __unicode__(self):
        return self.title

    class Meta:
        permissions = (
            ('sort_ad', 'Can sort the advertisements'),
        )


_MAX = 1024

@transaction.commit_manually
def sort_ad(pks):
    try:
        AD.objects.exclude(pk__in=pks).update(position=_MAX, visible=False)
        AD.objects.filter(pk__in=pks).update(visible=True)
        for i in range(0, len(pks)):
            ad = AD.objects.get(pk=pks[i])
            ad.position = i
            ad.save()
    except Exception as e:
        logger.exception(e)
        transaction.roll_back()
    else:
        transaction.commit()


@transaction.commit_manually
def set_ad_visible(pk):
    try:
        count = len(AD.objects.filter(visible=True))
        ad = AD.objects.get(pk=pk)
        ad.position = count
        ad.save()
    except Exception as e:
        logger.exception(e)
        transaction.roll_back()
    else:
        transaction.commit()


@transaction.commit_manually
def set_ad_invisible(pk):
    try:
        ad = AD.objects.get(pk=pk)
        with connection.connect() as cursor:
            cursor.execute("update ad_ad set position = position - 1 where position > ?", ad.position)
        ad.position = AD.objects.filter(visible=True).count()
        ad.visible = False
        ad.save()
    except Exception as e:
        logger.exception(e)
        transaction.roll_back
    else:
        transaction.commit()

