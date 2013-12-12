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
        empid_not_exists = 31415926

        package = 'com.tiantian.ttclock'
        package_not_exists = 'com.limijiaoyin.app'
        appid = 10000

        date_12_1 = date(year=2013, month=12, day=1)
        date_12_2 = date(year=2013, month=12, day=2)
        date_12_3 = date(year=2013, month=12, day=3)

        # emp(4) x package(2) x date(3) = cases(24)

        #same date same organization but not same package
        LogMeta(date=date_12_1, uid=emp_region.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_12_1, uid=emp_region.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()

        LogMeta(date=date_12_1, uid=emp_company.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_12_1, uid=emp_company.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()

        LogMeta(date=date_12_1, uid=emp_store.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_12_1, uid=emp_store.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()

        LogMeta(date=date_12_1, uid=empid_not_exists, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_12_1, uid=empid_not_exists, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()

        LogMeta(date=date_12_2, uid=emp_region.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_12_2, uid=emp_region.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()

        LogMeta(date=date_12_2, uid=emp_company.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_12_2, uid=emp_company.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()

        LogMeta(date=date_12_2, uid=emp_store.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_12_2, uid=emp_store.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()

        LogMeta(date=date_12_2, uid=empid_not_exists, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_12_2, uid=empid_not_exists, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()

        LogMeta(date=date_12_3, uid=emp_region.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_12_3, uid=emp_region.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()
        LogMeta(date=date_12_3, uid=emp_company.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_12_3, uid=emp_company.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()
        LogMeta(date=date_12_3, uid=emp_store.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_12_3, uid=emp_store.pk, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()
        LogMeta(date=date_12_3, uid=empid_not_exists, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package).save()
        LogMeta(date=date_12_3, uid=empid_not_exists, did=DEVICE_ID, 
                brand=BRAND, model=MODEL, appID=appid, appPkg=package_not_exists).save()

