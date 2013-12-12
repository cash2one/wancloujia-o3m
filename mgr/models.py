# coding: utf-8
from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType


def get_built_in_group_names():
    return [u"应用组", u"审核组", u"管理组", u"广告组"]


def is_group_built_in(group):
    return group.name in get_built_in_group_names()


class Staff(User):
    real_type =  models.ForeignKey(ContentType, editable=False)
    realname = models.CharField(verbose_name=u'真实姓名', max_length=20)
    phone = models.CharField(verbose_name=u'手机', max_length=20)
    tel = models.CharField(verbose_name=u'座机', max_length=20, blank=True)
    introduce = models.CharField(verbose_name=u'简介', max_length=200, blank=True)

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)

    def save(self, *args, **kwargs):
        if not self.id:
            self.real_type = self._get_real_type()
        super(Staff, self).save(*args, **kwargs)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))
    
    def __unicode__(self):
        return self.username


def cast_staff(user):
    return Staff.objects.get(pk=user.id).cast()


class Organization(models.Model):
    CODE_LENGTH_LIMIT = 20
    NAME_LENGTH_LIMIT = 200

    real_type = models.ForeignKey(ContentType, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.real_type = self._get_real_type()
        super(Organization, self).save(*args, **kwargs)

    def children(self):
        return []

    def descendants_and_self(self):
        return []

    def parent(self):
        return None

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def __unicode__(self):
        return self.cast().name


class NodeMixin:
    def belong_to(self, node):
        current = self
        while current and current.pk != node.pk:
            current = current.parent()

        return current is not None

    def parents(self):
        parents = []
        current = self.parent()
        while current is not None:
            parents.insert(0, current)
            current = current.parent()
        return parents

    def ancestor(self):
        current = self
        parent = current.parent()
        while parent:
            current = parent
            parent = current.parent()
        return current


class Region(Organization, NodeMixin):
    name = models.CharField(verbose_name=u'名称', unique=True, 
                            max_length=Organization.NAME_LENGTH_LIMIT)

    def children(self):
        return Company.objects.filter(region__pk=self.pk) if self.pk else []


    def descendants_and_self(self):
        if not self.pk:
            return []

        pks = [self.pk]
        companies = self.children()
        for company in companies:
            pks.append(company.pk)
        stores = Store.objects.filter(company__in=companies)
        for store in stores:
            pks.append(store.pk)
        return Organization.objects.filter(pk__in=pks)

    class Meta:
        verbose_name = u'大区'


class Company(Organization, NodeMixin):
    code = models.CharField(verbose_name=u'编码', unique=True, 
                            max_length=Organization.CODE_LENGTH_LIMIT)
    name = models.CharField(verbose_name=u'名称', unique=True, 
                            max_length=Organization.NAME_LENGTH_LIMIT)
    region = models.ForeignKey(Region, verbose_name=u'所属大区')

    def parent(self):
        return self.region

    def children(self):
        return Store.objects.filter(company__pk=self.pk) if self.pk else []

    def descendants_and_self(self):
        if not self.pk:
            return[]

        pks = [self.pk]
        for child in self.children():
            pks.append(child.pk)
        return Organization.objects.filter(pk__in=pks)

    class Meta:
        verbose_name = u'公司'


class Store(Organization, NodeMixin):
    code = models.CharField(verbose_name=u'编码', unique=True, 
                            max_length=Organization.CODE_LENGTH_LIMIT)
    name = models.CharField(verbose_name=u'名称', unique=True, 
                            max_length=Organization.NAME_LENGTH_LIMIT)
    company = models.ForeignKey(Company, verbose_name=u'所属公司')

    def parent(self):
        return self.company

    def descendants_and_self(self):
        return Organization.objects.filter(pk=self.pk) if self.pk else []

    class Meta:
        verbose_name = u'门店'
    

class Employee(Staff):
    organization = models.ForeignKey(Organization, verbose_name=u'所属机构')
    contact_person = models.CharField(verbose_name=u'联系人', max_length=20)
    contact_phone = models.CharField(verbose_name=u'联系电话', max_length=20)

    def __unicode__(self):
        return self.username

    def in_store(self):
        return self.organization.real_type == ContentType.objects.get_for_model(Store)

    def in_company(self):
        return self.organization.real_type == ContentType.objects.get_for_model(Company)

    def in_region(self):
        return self.organization.real_type == ContentType.objects.get_for_model(Region)

    def belong_to(self, org):
        organization = self.organization.cast()
        while organization and organization.pk != org.pk:
            organization = organization.parent()

        return organization is not None

    def org(self):
        return self.organization.cast()

    def organizations(self):
        organizations = []
        org = self.organization.cast()
        while org is not None:
            organizations.insert(0, org)
            org = org.parent()
        return organizations

    @classmethod
    def filter_by_organization(cls, org):
        orgs = org.descendants_and_self()
        return Employee.objects.filter(organization__in=orgs)


class Administrator(Staff):

    def save(self, *args, **kwargs):
        self.is_staff = True
        super(Administrator, self).save(args, kwargs)

    def __unicode__(self):
        return self.username


class SuperUser(Staff):
    
    def save(self, *args, **kwargs):
        self.is_superuser = True
        super(SuperUser, self).save(args, kwargs)

    def __unicode__(self):
        return self.username

