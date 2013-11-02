# coding: utf-8
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

_built_in_group_names = [u"应用组", u"审核组", u"专题组", u"广告组"]
def is_group_built_in(group):
    return group.name in _built_in_group_names


class Staff(User):
    real_type =  models.ForeignKey(ContentType, editable=False)
    realname = models.CharField(verbose_name=u'真实姓名', max_length=20)
    phone = models.CharField(verbose_name=u'手机', max_length=20)
    tel = models.CharField(verbose_name=u'座机', max_length=20, blank=True)
    introduce = models.CharField(verbose_name=u'简介', max_length=200, blank=True)

    DEFAULT_PASSWORD = 'suning'

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
    return Staff.objects.get(pk=user.id).cast()


class Organization(models.Model):
    name = models.CharField(verbose_name=u'名称', max_length=200)

    def __unicode__(self):
        return self.name


class Company(Organization):
    code = models.CharField(verbose_name=u'编码', max_length=20, unique=True)

    class Meta:
        verbose_name = '公司'


class Store(Organization):
    company = models.ForeignKey(Company, verbose_name=u'公司')
    code = models.CharField(verbose_name=u'编码', max_length=20, unique=True)

    class Meta:
        verbose_name = '门店'
    

class Employee(Staff):
    organization = models.ForeignKey(Organization, verbose_name=u'所属机构')
    #contact person type?
    contact_person = models.CharField(verbose_name=u'联系人', max_length=20)
    #contact person phone number type?
    contact_phone = models.CharField(verbose_name=u'联系电话', max_length=20)

    def __unicode__(self):
        return self.username


class Administrator(Staff):

    def save(self, *args, **kwargs):
        self.is_staff = True
        super(Administrator, self).save(args, kwargs)

    def __unicode__(self):
        return self.username


class SuperUser(Staff):
    
    def __unicode__(self):
        return self.username

