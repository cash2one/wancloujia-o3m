from datetime import datetime

from django.core.management.base import BaseCommand

from feedback.models import Feedback
from mgr.models import Staff

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        Feedback(date=datetime.now(), brand='HTC', model='HTC One',
                 user=Staff.objects.get(username='songwei'), content='what the hell?').save()


        
         
        
