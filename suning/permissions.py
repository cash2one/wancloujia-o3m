#coding: utf-8
from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from mgr.models import Organization, Staff
from ad.models import AD


_available_permissions = None


def get_available_permissions():
    global _available_permissions
    if _available_permissions is not None:
        return _available_permissions

    organization_type = ContentType.objects.get_for_model(Organization)
    group_type = ContentType.objects.get_for_model(Group)
    staff_type = ContentType.objects.get_for_model(Staff)
    ad_type = ContentType.objects.get_for_model(AD)
    _available_permissions = (
        (Permission.objects.get(content_type=organization_type, codename="add_organization").pk, u'添加组织'),
        (Permission.objects.get(content_type=organization_type, codename="change_organization").pk, u'编辑组织'),
        (Permission.objects.get(content_type=organization_type, codename="delete_organization").pk, u'删除组织'),
        (Permission.objects.get(content_type=staff_type, codename="add_staff").pk, u'添加用户'),
        (Permission.objects.get(content_type=staff_type, codename="change_staff").pk, u'编辑用户'),
        (Permission.objects.get(content_type=staff_type, codename="delete_staff").pk, u'删除用户'),
        (Permission.objects.get(content_type=ad_type, codename="add_ad").pk, u'添加广告'),
        (Permission.objects.get(content_type=ad_type, codename="change_ad").pk, u'编辑广告'),
        (Permission.objects.get(content_type=ad_type, codename="sort_ad").pk, u'排序广告'),
        (Permission.objects.get(content_type=ad_type, codename="delete_ad").pk, u'删除广告')
    )
    return _available_permissions


def get_permission_name(permission):
    for p in get_available_permissions():
        if p[0] == permission.pk: return p[1]
    return None

