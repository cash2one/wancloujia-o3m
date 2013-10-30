import logging
from datetime import datetime

from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        logger.debug("set all sessions expired")
        for session in Session.objects.all():
            session.expire_date = datetime.now()
            session.save()
