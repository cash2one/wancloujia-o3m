# coding: utf-8
from django.db import models
from django.contrib.auth.models import User, Group

class Organization(models.Model):
    code = models.CharField(verbose_name=u'编码', max_length=10)
    desc = models.CharField(verbose_name=u'描述', max_length=200)

    def __unicode__(self):
        return self.desc

class Company(Organization):
    pass

class Store(Organization):
    company = models.ForeignKey(Company, verbose_name=u'所属公司')

class Employee(User):
    organization = models.ForeignKey(Organization)
    phone = models.CharField(verbose_name=u'手机号码', max_length=20)
    introduce = models.CharField(verbose_name=u'简介', max_length=200)
    #contact person type?
    contact_person = models.CharField(verbose_name=u'联系人', max_length=20)
    #contact person phone number type?
    contact_phone = models.CharField(verbose_name=u'联系电话', max_length=20)

    def __unicode__(self):
        return self.username

class Administrator(User):

    def __unicode__(self):
        return self.username

class CustomGroup(Group):
    pass

