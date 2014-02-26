# coding: utf-8
from datetime import datetime
import logging

from django.db import models, connection, transaction
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from mgr.models import Staff


logger = logging.getLogger(__name__)


# Create your models here.
class Feedback(models.Model):
    date = models.DateTimeField()
    brand = models.CharField(verbose_name=u'pinpai', max_length=255, editable=False)
    model = models.CharField(verbose_name=u'jixing', max_length=16, editable=False)
    user = models.ForeignKey(Staff)
    content = models.CharField(max_length=128)

class HandledFeedback(models.Model):
    date = models.DateTimeField()
    brand = models.CharField(verbose_name=u'pinpai', max_length=255, editable=False)
    model = models.CharField(verbose_name=u'jixing', max_length=16, editable=False)
    user = models.ForeignKey(Staff)
    content = models.CharField(max_length=128)
    def from_feedback(self, feedback):
        if feedback:
            self.date = feedback.date
            self.brand = feedback.brand
            self.model = feedback.model
            self.user = feedback.user
            self.content = feedback.content

@transaction.commit_manually
def handle_feedback(pk):
    try:
        fb = Feedback.objects.get(pk=pk)
        hfb = HandledFeedback()
        hfb.from_feedback(fb)
        fb.delete()
        hfb.save()
    except Exception as e:
        logger.exception(e)
        transaction.roll_back()
        raise e
    else:
        transaction.commit()

@transaction.commit_manually
def delete_feedback(pk):
    try:
        fb = HandledFeedback.objects.get(pk=pk)
        fb.delete()
    except Exception as e:
        logger.exception(e)
        transaction.roll_back()
        raise e
    else:
        transaction.commit()