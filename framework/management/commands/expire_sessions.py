from datetime import datetime

from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        for session in Session.objects.all():
            session.expire_date = datetime.now()
            session.save()
