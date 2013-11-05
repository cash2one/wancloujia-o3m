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

    DEFAULT_PASSWORD = 'suning'

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

    def in_store(self):
        raise NotImplementedError()


def cast_staff(user):
    return Staff.objects.get(pk=user.id).cast()


class Organization(models.Model):
    name = models.CharField(verbose_name=u'名称', max_length=200)
    real_type = models.ForeignKey(ContentType, editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.real_type = self._get_real_type()
        super(Organization, self).save(*args, **kwargs)

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

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

    def in_store(self):
        return self.organization.real_type == ContentType.objects.get_for_model(Store)


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


_available_permissions = None


def get_available_permissions():
    global _available_permissions
    if _available_permissions is not None:
        return _available_permissions

    _organization_type = ContentType.objects.get_for_model(Organization)
    _group_type = ContentType.objects.get_for_model(Group)
    _staff_type = ContentType.objects.get_for_model(Staff)
    _available_permissions = (
        (Permission.objects.get(content_type=_organization_type, codename="add_organization").pk, u'添加组织'),
        (Permission.objects.get(content_type=_organization_type, codename="change_organization").pk, u'编辑组织'),
        (Permission.objects.get(content_type=_organization_type, codename="delete_organization").pk, u'删除组织'),
        (Permission.objects.get(content_type=_staff_type, codename="add_staff").pk, u'添加用户'),
        (Permission.objects.get(content_type=_staff_type, codename="change_staff").pk, u'编辑用户'),
        (Permission.objects.get(content_type=_staff_type, codename="delete_staff").pk, u'删除用户')
    )
    return _available_permissions


def get_permission_name(permission):
    for p in get_available_permissions():
        if p[0] == permission.pk: return p[1]
    return None

