from datetime import datetime, timedelta, date

from django.core.management.base import BaseCommand

from interface.models import LogMeta, InstalledAppLogEntity, DeviceLogEntity
from mgr.models import Employee
from app.models import App

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        LogMeta.objects.all().delete()
        InstalledAppLogEntity.objects.all().delete()
        DeviceLogEntity.objects.all().delete()

