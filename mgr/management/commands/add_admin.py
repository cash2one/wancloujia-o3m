from datetime import datetime

from django.core.management.base import BaseCommand
from mgr.models import Administrator

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        username = args[0]
        password = args[1] if len(args) > 1 else 'nameLR9969'
        admin = Administrator(username=username)
        admin.set_password(password)
        admin.is_staff = True
        admin.save()
