#!/usr/bin/env python
#coding: utf-8
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "og.settings")

    from app.models import Subject
    Subject.objects.all().delete()
    Subject(name=u'编辑推荐', code='recommends').save()
    Subject(name=u'单机游戏', code='games').save()
    Subject(name=u'礼包放送', code='gifts').save()
    Subject(name=u'热门网游', code='onlinegames').save()
    Subject(name=u'装机必备', code='zone1').save()
    Subject(name=u'上升最快', code='zone2').save()

    from ad.models import AD
    AD.objects.all().delete()
    AD(title=u'主广告位', link=u'http://baidu.com', cover='').save()
    AD(title=u'副广告位', link=u'http://baidu.com', cover='').save()

