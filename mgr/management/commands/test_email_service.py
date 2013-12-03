from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mgr.models import Administrator
from suning.service import notify

class Command(BaseCommand):
    
    def handle(self, *args, **options):
    	user = User()
    	user.username = 'jarvis'
    	user.realname = 'jarvis'
    	user.email = 'yuhan534@126.com'
    	notify(user, 'bachisback')
