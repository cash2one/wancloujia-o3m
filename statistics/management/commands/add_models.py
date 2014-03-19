from datetime import datetime
import traceback
import sys
from datetime import datetime
from django.core.management.base import BaseCommand

from statistics.models import BrandModel

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        BrandModel(brand="test", model="MI 2S").save();
        BrandModel(brand="test", model="8085N").save();
