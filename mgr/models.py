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

    def parent(self):
        return None

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def __unicode__(self):
        return self.cast().name


class Region(Organization):
    name = models.CharField(verbose_name=u'名称', unique=True, 
                            max_length=Organization.NAME_LENGTH_LIMIT)

    def children(self):
        return Company.objects.filter(region__pk=self.pk) if self.pk else []

    class Meta:
        verbose_name = u'大区'


class Company(Organization):
    code = models.CharField(verbose_name=u'编码', unique=True, 
                            max_length=Organization.CODE_LENGTH_LIMIT)
    name = models.CharField(verbose_name=u'名称', unique=True, 
                            max_length=Organization.NAME_LENGTH_LIMIT)
    region = models.ForeignKey(Region, verbose_name=u'所属大区')

    def parent(self):
        return self.region

    def children(self):
        return Store.objects.filter(company__pk=self.pk) if self.pk else []

    class Meta:
        verbose_name = u'公司'


class Store(Organization):
    code = models.CharField(verbose_name=u'编码', unique=True, 
                            max_length=Organization.CODE_LENGTH_LIMIT)
    name = models.CharField(verbose_name=u'名称', unique=True, 
                            max_length=Organization.NAME_LENGTH_LIMIT)
    company = models.ForeignKey(Company, verbose_name=u'所属公司')

    def parent(self):
        return self.company

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

    def in_region(self):
        return self.organization.real_type == ContentType.objects.get_for_model(Region)


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

