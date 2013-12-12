#coding: utf-8
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from interface.models import LogMeta
from mgr.models import Region, Store, Company, Employee
from views import query_employee, query_regions, query_companies, query_stores


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

