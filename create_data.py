#!/usr/bin/env python
#coding: utf-8
import os
import sys
DEFAULT_IMAGE = 'http://placehold.it/350x150'


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "og.settings")

    #from app.models import Subject
    #Subject.objects.all().delete()
    #Subject(name=u'编辑推荐', code='recommends').save()
    #Subject(name=u'单机游戏', code='games').save()
    #Subject(name=u'礼包放送', code='gifts').save()
    #Subject(name=u'热门网游', code='onlinegames').save()
    #Subject(name=u'装机必备', code='zone1').save()
    #Subject(name=u'上升最快', code='zone2').save()

    #from ad.models import AD
    #AD.objects.all().delete()
    #AD(title=u'主广告位', link=u'http://baidu.com', cover=DEFAULT_IMAGE).save()
    #AD(title=u'副广告位', link=u'http://baidu.com', cover=DEFAULT_IMAGE).save()

    from app.models import Plate
    Plate.objects.all().delete()
    Plate(position='top1', name='top1', cover=DEFAULT_IMAGE).save()
    Plate(position='top2', name='top2', cover=DEFAULT_IMAGE).save()
    Plate(position='top3', name='top3', cover=DEFAULT_IMAGE).save()
    Plate(position='top4', name='top4', cover=DEFAULT_IMAGE).save()
    Plate(position='top5', name='top5', cover=DEFAULT_IMAGE).save()
    Plate(position='top6', name='top6', cover=DEFAULT_IMAGE).save()
    Plate(position='top7', name='top7', cover=DEFAULT_IMAGE).save()
    Plate(position='top8', name='top8', cover=DEFAULT_IMAGE).save()
    Plate(position='top9', name='top9', cover=DEFAULT_IMAGE).save()
    Plate(position='middle', name='middle', cover=DEFAULT_IMAGE).save()
    Plate(position='bottom1', name='bottom1', cover=DEFAULT_IMAGE).save()
    Plate(position='bottom2', name='bottom2', cover=DEFAULT_IMAGE).save()
    Plate(position='bottom3', name='bottom3', cover=DEFAULT_IMAGE).save()

