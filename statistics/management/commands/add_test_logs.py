from datetime import datetime, timedelta, date

from django.core.management.base import BaseCommand

from interface.models import LogMeta, InstalledAppLogEntity
from mgr.models import Employee, Region, Company, Store
from app.models import App

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        #self.add_test_logs_for_flow()
        self.add_test_logs_for_installed_capacity()

    def add_test_logs_for_installed_capacity(self):
        region = Region.objects.get(name='region')
        company = Company.objects.get(name='company')
        store = Store.objects.get(name='store')

        emp_region = Employee.objects.get(username='emp_region')
        emp_company = Employee.objects.get(username='emp_company')
        emp_store = Employee.objects.get(username='emp_store')
        empid_not_exists = 31415926

        package = 'com.tiantian.ttclock'
        package_not_exists = 'com.limijiaoyin.app'
        appid = 10000
        appname = 'ttclock'

        date_12_1 = date(year=2013, month=12, day=1)

        # emp(4) x package(2) x date(1) = cases(8)
        InstalledAppLogEntity(date=date_12_1, uid=emp_store.pk, store=store.pk, company=company.pk, region=region.pk, popularize=True,
                appName=appname, appID=appid, appPkg=package, installedTimes=1).save()
        InstalledAppLogEntity(date=date_12_1, uid=emp_store.pk, store=store.pk, company=company.pk, region=region.pk, popularize=True,
                appName=appname, appID=appid, appPkg=package_not_exists, installedTimes=1).save()

        InstalledAppLogEntity(date=date_12_1, uid=emp_company.pk, company=company.pk, region=region.pk, popularize=True,
                appName=appname, appID=appid, appPkg=package, installedTimes=1).save()
        InstalledAppLogEntity(date=date_12_1, uid=emp_company.pk, company=company.pk, region=region.pk, popularize=True,
                appName=appname, appID=appid, appPkg=package_not_exists, installedTimes=1).save()

        InstalledAppLogEntity(date=date_12_1, uid=emp_region.pk, region=region.pk, popularize=True,
                appName=appname, appID=appid, appPkg=package, installedTimes=1).save()
        InstalledAppLogEntity(date=date_12_1, uid=emp_region.pk, region=region.pk, popularize=True,
                appName=appname, appID=appid, appPkg=package_not_exists, installedTimes=1).save()

        InstalledAppLogEntity(date=date_12_1, uid=empid_not_exists, store=1, company=1, region=1, popularize=True,
                appName=appname, appID=appid, appPkg=package, installedTimes=1).save()
        InstalledAppLogEntity(date=date_12_1, uid=empid_not_exists, store=1, company=1, region=1, popularize=True,
                appName=appname, appID=appid, appPkg=package_not_exists, installedTimes=1).save()
        

    def add_test_logs_for_flow(self):
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

