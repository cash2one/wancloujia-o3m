import random
from datetime import datetime, timedelta, date

from django.core.management.base import BaseCommand

from interface.models import LogMeta, InstalledAppLogEntity
from interface.models import DeviceLogEntity, UserDeviceLogEntity
from mgr.models import Employee, Region, Company, Store
from app.models import App

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        self.add_test_logs_for_flow()
        self.add_test_logs_for_installed_capacity()
        self.add_test_logs_for_device_stat()
        self.add_test_logs_for_org()

    def add_test_logs_for_org(self):
        # emp(4) x model(1) x device(1) date(1) x app(1) = cases(4)
        region = Region.objects.get(name='region')
        company = Company.objects.get(name='company')
        store = Store.objects.get(name='store')
        emp_region = Employee.objects.get(username='emp_region')
        emp_company = Employee.objects.get(username='emp_company')
        emp_store = Employee.objects.get(username='emp_store')
        empid_not_exists = 31415926

        appPkg = 'com.tiantian.ttclock'
        appID = 1000
        appName = 'ttclock'
        d = date(year=2013, month=12, day=1)

        UserDeviceLogEntity(date=d,  uid=emp_region.pk, 
                           region=region.pk, 
                           deviceCount=1, popularizeAppCount=1, appCount=2).save()

        UserDeviceLogEntity(date=d,  uid=emp_company.pk, 
                           region=region.pk, company=company.pk,
                           deviceCount=1, popularizeAppCount=1, appCount=2).save()

        UserDeviceLogEntity(date=d,  uid=emp_store.pk, 
                           region=region.pk, company=company.pk, store=store.pk,
                           deviceCount=1, popularizeAppCount=1, appCount=2).save()

        UserDeviceLogEntity(date=d,  uid=empid_not_exists, 
                           deviceCount=1, popularizeAppCount=1, appCount=2).save()


    def add_test_logs_for_device_stat(self):
        htc = 'hTC'
        htc_one = 'hTC One'
        htc_butterfly = 'hTC butterfly'
        self.add_test_logs_for_device_stat_by_model_device(htc, htc_one, 1)
        self.add_test_logs_for_device_stat_by_model_device(htc, htc_butterfly, 2)

        
    def add_test_logs_for_device_stat_by_model_device(self, brand, model, device):
        # emp(4) x model(1) x device(1) date(1) x app(1) = cases(4)
        region = Region.objects.get(name='region')
        company = Company.objects.get(name='company')
        store = Store.objects.get(name='store')
        emp_region = Employee.objects.get(username='emp_region')
        emp_company = Employee.objects.get(username='emp_company')
        emp_store = Employee.objects.get(username='emp_store')
        empid_not_exists = 31415926

        appPkg = 'com.tiantian.ttclock'
        appID = 1000
        appName = 'ttclock'
        d = date(year=2013, month=12, day=1)

        DeviceLogEntity(date=d, brand=brand, model=model, 
                        uid=emp_region.pk, region=region.pk, 
                        appID=appID, appPkg=appPkg, appName=appName,
                        did=device, popularizeAppCount=1, appCount=2).save()

        DeviceLogEntity(date=d, brand=brand, model=model, 
                        uid=emp_company.pk, company=company.pk, region=region.pk, 
                        appID=appID, appPkg=appPkg, appName=appName,
                        did=device, popularizeAppCount=1, appCount=2).save()

        DeviceLogEntity(date=d, brand=brand, model=model, 
                        uid=emp_store.pk, store=store.pk, 
                        company=company.pk, region=region.pk, 
                        appID=appID, appPkg=appPkg, appName=appName,
                        did=device, popularizeAppCount=1, appCount=2).save()

        DeviceLogEntity(date=d, brand=brand, model=model, 
                        uid=empid_not_exists,
                        appID=appID, appPkg=appPkg, appName=appName,
                        did=device, popularizeAppCount=1, appCount=2).save() 
        
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

        InstalledAppLogEntity(date=date_12_1, uid=empid_not_exists, popularize=True,
                appName=appname, appID=appid, appPkg=package, installedTimes=1).save()
        InstalledAppLogEntity(date=date_12_1, uid=empid_not_exists, popularize=True,
                appName=appname, appID=appid, appPkg=package_not_exists, installedTimes=1).save()
        

    def add_test_logs_for_flow(self):
        date_12_1 = date(year=2013, month=12, day=1)
        self.add_test_logs_for_flow_by_date_brand_model(date_12_1, 'hTC', 'hTC One S')
        self.add_test_logs_for_flow_by_date_brand_model(date_12_1, 'Google', 'Google Nexus 5')

    def add_test_logs_for_flow_by_date_brand_model(self, date, brand, model):
        device = random.randint(10 * 13, 10 * 14-1)

        emp_region = Employee.objects.get(username='emp_region')
        emp_company = Employee.objects.get(username='emp_company')
        emp_store = Employee.objects.get(username='emp_store')
        empid_not_exists = 31415926

        package = 'com.tiantian.ttclock'
        package_not_exists = 'com.limijiaoyin.app'
        appid = 10000

        # emp(4) x package(2) x date(3) x brand(1) x model(1) = cases(12)
        LogMeta(date=date, uid=emp_region.pk, did=device, 
                brand=brand, model=model, appID=appid, appPkg=package).save()
        LogMeta(date=date, uid=emp_region.pk, did=device, 
                brand=brand, model=model, appID=appid, appPkg=package_not_exists).save()

        LogMeta(date=date, uid=emp_company.pk, did=device, 
                brand=brand, model=model, appID=appid, appPkg=package).save()
        LogMeta(date=date, uid=emp_company.pk, did=device, 
                brand=brand, model=model, appID=appid, appPkg=package_not_exists).save()

        LogMeta(date=date, uid=emp_store.pk, did=device, 
                brand=brand, model=model, appID=appid, appPkg=package).save()
        LogMeta(date=date, uid=emp_store.pk, did=device, 
                brand=brand, model=model, appID=appid, appPkg=package_not_exists).save()

        LogMeta(date=date, uid=empid_not_exists, did=device, 
                brand=brand, model=model, appID=appid, appPkg=package).save()
        LogMeta(date=date, uid=empid_not_exists, did=device, 
                brand=brand, model=model, appID=appid, appPkg=package_not_exists).save()
