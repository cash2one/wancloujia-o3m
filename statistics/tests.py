#coding: utf-8
from datetime import date

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from interface.models import LogMeta
from mgr.models import Region, Store, Company, Employee
from views import query_employee, query_regions, query_companies, query_stores
from ajax import AdminFilter, UserPermittedFilter, UserUnpermittedFilter
from ajax import available_levels, titles_for_org_stat


def _equal(emp_qs, emp_arr):
    qs_dict = {}
    for emp in emp_qs:
        qs_dict[emp.username] = emp

    arr_dict = {}
    for emp in emp_arr:
        arr_dict[emp.username] = emp

    return qs_dict == arr_dict


class TestEmployeeView(TestCase):

    def setUp(self):
        self.region = Region(name='region')
        self.region.save()

        self.company1 = Company(name='compnay1', region=self.region)
        self.company1.save()
        self.store1 = Store(code='1', name='test_1', company=self.company1)
        self.store1.save()
        self.emp = Employee(username='test_emp', organization=self.company1)
        self.emp.save()

        self.company2 = Company(code='2',name='company2', region=self.region)
        self.company2.save()
        self.store2 = Store(code='2', name='test_2', company=self.company2)
        self.store2.save()
        self.store3 = Store(code='3', name='test_3', company=self.company2)
        self.store3.save()
        self.store4 = Store(code='4', name='test_4', company=self.company2)
        self.store4.save()
        self.emp2 = Employee(username='test_emp2', organization=self.store2)
        self.emp2.save()
        self.emp3 = Employee(username='test_emp3', organization=self.store2)
        self.emp3.save()

        self.admin = User(username='admin', is_staff=True)
        self.admin.save()


    def test_query_employee(self):
        emps = query_employee(self.emp, None)
        self.assertTrue(len(emps) == 0)

        emps = query_employee(self.admin, self.company2)
        self.assertTrue(_equal(emps, [self.emp2, self.emp3]))

        emps = query_employee(self.emp, self.company1)
        self.assertTrue(_equal(emps, [self.emp]))

        emps = query_employee(self.emp, self.company2)
        self.assertTrue(len(emps) == 0)
        

class TestQueryRegions(TestCase):
    def setUp(self):
        log_type = ContentType.objects.get_for_model(LogMeta)
        permission = Permission.objects.get(content_type=log_type, 
                                            codename='view_organization_statistics')

        self.admin = User(username='admin', is_staff=True)
        self.admin.save()
        self.region1 = Region(name='region1')
        self.region1.save()
        self.emp = Employee(username='test_emp', organization=self.region1)
        self.emp.save()
        self.emp.user_permissions=[permission]

        self.region2 = Region(name='region2')
        self.region2.save()

        self.emp_no_perm = Employee(username='test_emp_no_perm', organization=self.region1)
        self.emp_no_perm.save()

    def test_query_regions(self):
        regions = query_regions(self.admin)
        self.assertItemsEqual(regions, Region.objects.all())

        regions = query_regions(self.emp_no_perm)
        self.assertTrue(len(regions) == 0)

        regions = query_regions(self.emp)
        self.assertItemsEqual(regions, [self.region1])


class TestQueryCompanies(TestCase):
    def setUp(self):
        log_type = ContentType.objects.get_for_model(LogMeta)
        permission = Permission.objects.get(content_type=log_type, 
                                            codename='view_organization_statistics')

        self.admin = User(username='admin', is_staff=True)
        self.admin.save()

        self.region1 = Region(name='region1')
        self.region1.save()
        self.emp_region1_1 = Employee(username='test_emp', organization=self.region1)
        self.emp_region1_1.save()
        self.emp_region1_1.user_permissions = [permission]

        self.emp_no_perm = Employee(username='test_emp_no_perm', organization=self.region1)
        self.emp_no_perm.save()

        self.company = Company(code='1001', name='company1', region = self.region1)
        self.company.save()

        self.store = Store(code='10011001', name='store1', company=self.company)
        self.store.save()
        self.emp_store = Employee(username='test_emp2', organization=self.store)
        self.emp_store.save()
        self.emp_store.user_permissions = [permission]

    def test_query_companies(self):
        companies = query_companies(self.admin, "")
        self.assertTrue(len(companies) == 0)

        companies = query_companies(self.emp_no_perm, self.region1.pk)
        self.assertTrue(len(companies) == 0)

        companies = query_companies(self.admin, self.region1.pk)
        self.assertItemsEqual(companies, [self.company])

        companies = query_companies(self.emp_region1_1, self.region1.pk)
        self.assertItemsEqual(companies, [self.company])

        companies = query_companies(self.emp_store, self.region1.pk)
        self.assertTrue(len(companies) == 0)


class TestQueryStores(TestCase):
    def setUp(self):
        log_type = ContentType.objects.get_for_model(LogMeta)
        permission = Permission.objects.get(content_type=log_type, 
                                            codename='view_organization_statistics')

        self.admin = User(username='admin', is_staff=True)
        self.admin.save()

        self.region1 = Region(name='region1')
        self.region1.save()
        self.emp_region1_1 = Employee(username='test_emp', organization=self.region1)
        self.emp_region1_1.save()
        self.emp_region1_1.user_permissions = [permission]

        self.emp_no_perm = Employee(username='test_emp_no_perm', organization=self.region1)
        self.emp_no_perm.save()

        self.company = Company(code='1001', name='company1', region = self.region1)
        self.company.save()
        self.emp_company = Employee(username='test_emp_company', organization=self.company)
        self.emp_company.save()
        self.emp_company.user_permissions = [permission]

        self.store = Store(code='10011001', name='store1', company=self.company)
        self.store.save()
        self.emp_store = Employee(username='test_emp2', organization=self.store)
        self.emp_store.save()
        self.emp_store.user_permissions = [permission]

    def test_query_stores(self):
        stores = query_stores(self.admin, "")
        self.assertTrue(len(stores) == 0)

        stores = query_stores(self.admin, self.company.pk)
        self.assertItemsEqual(stores, [self.store])

        stores = query_companies(self.emp_no_perm, self.company.pk)
        self.assertTrue(len(stores) == 0)

        stores = query_stores(self.emp_company, self.company.pk)
        self.assertItemsEqual(stores, [self.store])

        stores = query_stores(self.emp_store, self.company.pk)
        self.assertTrue(len(stores) == 0)


class TestUserFilter(TestCase):
    def setUp(self):
        self.region = Region(name='region')
        self.region.save()
        self.company = Company(code='1001', name='company', region=self.region)
        self.company.save()
        self.store = Store(code='10011001', name='store', company=self.company)
        self.store.save()

        self.emp_region = Employee(username='emp_region', organization=self.region)
        self.emp_region.save()
        self.emp_company = Employee(username='emp_company', organization=self.company)
        self.emp_company.save()
        self.emp_store = Employee(username='emp_store', organization=self.store)
        self.emp_store.save()
        self.empid_not_exists = 31415926

        package = 'com.tiantian.ttclock'
        appid = 10000

        d = date(year=2013, month=12, day=1)
        self.log1 = LogMeta(date=d, uid=self.emp_region.pk, appID=appid, appPkg=package)
        self.log1.save()
        self.log2 = LogMeta(date=d, uid=self.emp_company.pk, appID=appid, appPkg=package)
        self.log2.save()
        self.log3 = LogMeta(date=d, uid=self.emp_store.pk, appID=appid, appPkg=package)
        self.log3.save()
        self.logs = LogMeta.objects.all()

    def test_admin_filter(self):
        filter = AdminFilter(self.logs, None, self.company.pk, None, None)
        logs = filter.filter()
        self.assertItemsEqual([self.log2, self.log3], logs)

        filter = AdminFilter(self.logs, None, None, None, self.emp_store.pk)
        logs = filter.filter()
        self.assertItemsEqual([self.log3], logs)

        filter = AdminFilter(self.logs, None, None, None, None)
        logs = filter.filter()
        self.assertItemsEqual(logs, logs)

    def test_user_permitted_filter(self):
        filter = UserPermittedFilter(self.emp_company, self.logs,  
                                     None, None, None, self.emp_company.pk)
        logs = filter.filter()
        self.assertItemsEqual([self.log2], logs)

        filter = UserPermittedFilter(self.emp_company, self.logs, 
                                     None, None, None, self.emp_region.pk)
        logs = filter.filter()
        self.assertTrue(len(logs) == 0)

        filter = UserPermittedFilter(self.emp_company, self.logs,
                                     None, None, self.store.pk, None)
        logs = filter.filter()
        self.assertItemsEqual([self.log3], logs)

        filter = UserPermittedFilter(self.emp_company, self.logs, 
                                     self.emp_region.pk, None, None, None)
        logs = filter.filter()
        self.assertTrue(len(logs) == 0)

        filter = UserPermittedFilter(self.emp_company, self.logs, 
                                     None, None, None, None)
        logs = filter.filter()
        self.assertItemsEqual([self.log2, self.log3], logs)


    def test_user_unpermitted_filter(self):
        filter = UserUnpermittedFilter(self.logs, self.emp_store.pk)
        logs = filter.filter()
        self.assertItemsEqual([self.log3], logs)


class TestLevels(TestCase):

    def test_available_levels(self):
        self.assertItemsEqual(['region', 'company'], available_levels('region', 'company'))
        self.assertItemsEqual(['company', 'store', 'emp'], available_levels('company', 'emp'))


class TestTitlesForOrgStat(TestCase):
    
    def test_titles_for_org_stat(self):
        expected = [u'大区', u'公司编码', u'公司名称', u'机器台数', u'推广数', u'安装总数']
        self.assertItemsEqual(expected, titles_for_org_stat('region', 'company'))

