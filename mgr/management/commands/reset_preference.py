from datetime import datetime

from django.core.management.base import BaseCommand
from mgr.models import Preference, PREFERENCE_DEFAULT_COLOR, PREFERENCE_DEFAULT_NAVBAR_COLOR

class Command(BaseCommand):
    
    def handle(self, *args, **options):
		try: 
			preference = Preference.objects.get(pk=1)
		except:
			preference = Preference(pk=1)

		preference.color = PREFERENCE_DEFAULT_COLOR
		preference.navbar_color = PREFERENCE_DEFAULT_NAVBAR_COLOR
		preference.vendor_prefix = ''
		preference.favicon = None 
		preference.logo = None
		preference.save()
	

