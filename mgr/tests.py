#coding: utf-8
from models import Region, Company, Store, Employee

from django.test import TestCase


class TestOrganizationAncestor(TestCase):
    def setUp(self):
        self.region = Region(name='test_region')
        self.region.save()
        self.company = Company(code='1001', name='test_company', region=self.region)
        self.company.save()

        self.store = Store(code='10011001', name='test_store', company=self.company)
        self.store.save()

    def test_ancestor(self):
        self.assertTrue(self.region.pk == self.company.ancestor().pk)
        self.assertTrue(self.region.pk == self.store.ancestor().pk)


class TestEmployeeOrganizations(TestCase):
    def setUp(self):
        self.region = Region(name='test_region')
        self.region.save()
        self.company = Company(code='1001', name='test_company', region=self.region)
        self.company.save()

        self.store = Store(code='10011001', name='test_store', company=self.company)
        self.store.save()

        self.emp_region = Employee(username='emp_region', organization = self.region)
        self.emp_company = Employee(username='emp_company', organization = self.company)
        self.emp_store = Employee(username='emp_store', organization = self.store)

    def test_organizations(self):
        organizations = self.emp_region.organizations()
        self.assertEquals([self.region], organizations)
        organizations = self.emp_company.organizations()
        self.assertEquals([self.region, self.company], organizations)
        organizations = self.emp_store.organizations()
        self.assertEquals([self.region, self.company, self.store], organizations)

    def test_in_xxx_org(self):
        # employee in region
        self.assertTrue(self.emp_region.in_region())
        self.assertFalse(self.emp_region.in_company())
        self.assertFalse(self.emp_region.in_store())

        # employee in company
        self.assertFalse(self.emp_company.in_region())
        self.assertTrue(self.emp_company.in_company())
        self.assertFalse(self.emp_company.in_store())

        # employee in company
        self.assertFalse(self.emp_store.in_region())
        self.assertFalse(self.emp_store.in_company())
        self.assertTrue(self.emp_store.in_store())

    def test_org(self):
        self.assertEqual(self.emp_region.org(), self.region)
        self.assertEqual(self.emp_company.org(), self.company)
        self.assertEqual(self.emp_store.org(), self.store)

