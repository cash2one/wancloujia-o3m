from datetime import datetime

from django.core.management.base import BaseCommand
from mgr.models import SuperUser

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        username = args[0]
        password = args[1] if len(args) > 1 else 'nameLR9969'
        su = SuperUser(username=username)
        su.set_password(password)
        su.save()
