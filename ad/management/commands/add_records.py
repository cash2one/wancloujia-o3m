from datetime import datetime

from django.core.management.base import BaseCommand

from ad.models import AD

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        for i in range(0, 1000):
            record = AD(title='test', offline_date=datetime.now())
            record.save()
        
         
        
