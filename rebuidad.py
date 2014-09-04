#!/usr/bin/env python
#coding: utf-8
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "og.settings")

    from interface.models import AdsLogEntity, AdsStaEntity
    import datetime
    import logging
    logger = logging.getLogger(__name__)

    index = 1
    while(index <= 14484947):
        log = AdsLogEntity.objects.get(pk=index)
        index += 1
        print log.datetime.date()
        print log.id
        logger.info(log.id)
        date = log.datetime.date()
        obj, created = AdsStaEntity.objects.get_or_create(datetime=date)
        op = log.op
        title = log.adTitle
        if op == 'view' and title == u'主广告位':
            obj.view = obj.view + 1
            obj.save()
            continue
        if op == 'click':
            if title == u'主广告位':
                obj.main_click = obj.main_click + 1
                obj.save()
                continue
            else:
                obj.side_click = obj.side_click + 1
                obj.save()
                continue



