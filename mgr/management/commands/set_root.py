from datetime import datetime

from django.core.management.base import BaseCommand
from mgr.models import SuperUser

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        username = args[0]
        password = args[1] if len(args) > 1 else 'nameLR9969'
        su_list = SuperUser.objects.all()
        su = su_list[0] if len(su_list) > 0 else SuperUser(username=username)
        su.username = username
        su.set_password(password)
        su.is_superuser = True
        su.save()
