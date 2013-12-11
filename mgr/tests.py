#coding: utf-8
from models import Region, Company, Store

from django.test import TestCase


class SimpleTest(TestCase):
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

