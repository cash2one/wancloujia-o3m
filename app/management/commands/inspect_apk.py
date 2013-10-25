import logging
import traceback
from pprint import pprint
from os.path import abspath, basename, join
from datetime import datetime

from django.core.management.base import BaseCommand
from app import apk

logger = logging.getLogger(__name__)

def _read_icon_cb(icon, f): 
    bytes = f.read()
    name = basename(icon)
    with open(join("..", name), "w") as dest:
        dest.write(bytes)

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        path = abspath(args[0])
        apk_info = apk.inspect(path)
        pprint(vars(apk_info))
        print "app name: %s" % apk_info.getAppName()
        print "app icon: %s" % apk_info.getIcon()
        print "package name: %s" % apk_info.getPackageName()
        print "package size: %d" % apk_info.getPackageSize()
        print "min sdk version: %d" % apk_info.getMinSdkVersion()
        minAndroidVersion = apk.apiLevelToAndroidVersion(apk_info.getMinSdkVersion())
        print "min android version: android-%s" %  minAndroidVersion
        print "target sdk version: %d" % apk_info.getTargetSdkVersion()
        targetAndroidVersion = apk.apiLevelToAndroidVersion(apk_info.getTargetSdkVersion())
        print "target android version: android-%s" % targetAndroidVersion
        apk.read_icon(path, _read_icon_cb)
        
