from datetime import datetime, timedelta, date

from django.core.management.base import BaseCommand

from interface.models import LogMeta
from mgr.models import Employee
from app.models import App

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        DEVICE_ID = 'device_id?'
        BRAND = 'brand?'
        MODEL = 'model?'

        emp_region = Employee.objects.get(username='emp_region')
        emp_company = Employee.objects.get(username='emp_company')
        emp_store = Employee.objects.get(username='emp_store')
        empid_not_exists = 10000

        package = 'com.tiantian.ttclock'
        package_not_exists = 'sdfljsdlfjsldfj'
        appid = 10000

        date_1_1 = date(year=2013, month=1, day=1)
        date_2_1 = date(year=2013, month=2, day=1)
        date_3_1 = date(year=2013, month=3, day=1)

        LogMeta(date=date_1_1, uid=emp_region.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_1_1, uid=emp_region.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()
        LogMeta(date=date_1_1, uid=emp_company.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_1_1, uid=emp_company.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()
        LogMeta(date=date_1_1, uid=emp_store.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_1_1, uid=emp_store.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()
        LogMeta(date=date_1_1, uid=empid_not_exists, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_1_1, uid=empid_not_exists, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()

        LogMeta(date=date_2_1, uid=emp_region.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_2_1, uid=emp_region.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()
        LogMeta(date=date_2_1, uid=emp_company.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_2_1, uid=emp_company.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()
        LogMeta(date=date_2_1, uid=emp_store.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_2_1, uid=emp_store.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()
        LogMeta(date=date_2_1, uid=empid_not_exists, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_2_1, uid=empid_not_exists, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()

        LogMeta(date=date_3_1, uid=emp_region.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_3_1, uid=emp_region.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()
        LogMeta(date=date_3_1, uid=emp_company.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_3_1, uid=emp_company.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()
        LogMeta(date=date_3_1, uid=emp_store.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_3_1, uid=emp_store.pk, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()
        LogMeta(date=date_3_1, uid=empid_not_exists, did=DEVICE_ID, brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_3_1, uid=empid_not_exists, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()

