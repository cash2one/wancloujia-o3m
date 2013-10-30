# coding: utf-8
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

class Staff(User):
    real_type =  models.ForeignKey(ContentType, editable=False)
    realname = models.CharField(verbose_name=u'真实姓名', max_length=20)
    phone = models.CharField(verbose_name=u'手机', max_length=20)
    tel = models.CharField(verbose_name=u'座机', max_length=20)
    introduce = models.CharField(verbose_name=u'简介', max_length=200)

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.id)

    def save(self, *args, **kwargs):
        if not self.id:
            self.real_type = self._get_real_type()
        super(Staff, self).save(*args, **kwargs)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))
    
    def __unicode__(self):
        return self.username


def cast_staff(user):
    return Staff.objects.get(pk=user.id)


class Organization(models.Model):
    code = models.CharField(verbose_name=u'编码', max_length=10)
    desc = models.CharField(verbose_name=u'描述', max_length=200)

    def __unicode__(self):
        return self.desc


class Company(Organization):
    pass


class Store(Organization):
    company = models.ForeignKey(Company, verbose_name=u'所属公司')


class Employee(Staff):
    organization = models.ForeignKey(Organization)
    #contact person type?
    contact_person = models.CharField(verbose_name=u'联系人', max_length=20)
    #contact person phone number type?
    contact_phone = models.CharField(verbose_name=u'联系电话', max_length=20)

    def __unicode__(self):
        return self.username


class Administrator(Staff):

    def __unicode__(self):
        return self.username


class SuperUser(Staff):
    
    def __unicode__(self):
        return self.username


class CustomGroup(Group):
    verbose_name = models.CharField(max_length=80)


