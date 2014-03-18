import traceback
import sys
from datetime import datetime
from django.core.management.base import BaseCommand
from modelmgr.models import Model

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        path = args[0]
        with open(path, "r") as file:
            for line in file:
                parts = line.split()
                model = Model()
                model.name = parts[1]
                model.ua = parts[2]

                try:
                    model.save()
                except Exception as e:
                    sys.stderr.write("fail to add model " + model.name + "\n")
                    sys.stderr.write(str(e) + "\n")
