from datetime import datetime

from django.core.management.base import BaseCommand
from modelmgr.models import Model

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        Model.objects.all().delete()
