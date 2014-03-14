#coding: utf-8
from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from mgr.models import Organization, Staff
from ad.models import AD
from app.models import App, Subject
from oplog.models import op_log
from interface.models import LogMeta, LogEntity


_available_permissions = None


def get_available_permissions():
    global _available_permissions
    if _available_permissions is not None:
        return _available_permissions

    organization_type = ContentType.objects.get_for_model(Organization)
    group_type = ContentType.objects.get_for_model(Group)
    staff_type = ContentType.objects.get_for_model(Staff)
    ad_type = ContentType.objects.get_for_model(AD)
    app_type = ContentType.objects.get_for_model(App)
    subject_type = ContentType.objects.get_for_model(Subject)
    log_meta_type = ContentType.objects.get_for_model(LogMeta)
    log_entity_type = ContentType.objects.get_for_model(LogEntity)
    oplog_type = ContentType.objects.get_for_model(op_log)

    _available_permissions = (
        (Permission.objects.get(content_type=organization_type, codename="add_organization").pk, u'添加组织'),
        (Permission.objects.get(content_type=organization_type, codename="change_organization").pk, u'编辑组织'),
        (Permission.objects.get(content_type=organization_type, codename="delete_organization").pk, u'删除组织'),

        (Permission.objects.get(content_type=staff_type, codename="add_staff").pk, u'添加用户'),
        (Permission.objects.get(content_type=staff_type, codename="change_staff").pk, u'编辑用户'),
        (Permission.objects.get(content_type=staff_type, codename="delete_staff").pk, u'删除用户'),

        #(Permission.objects.get(content_type=ad_type, codename="add_ad").pk, u'添加广告'),
        #(Permission.objects.get(content_type=ad_type, codename="change_ad").pk, u'编辑广告'),
        #(Permission.objects.get(content_type=ad_type, codename="sort_ad").pk, u'调整广告顺序'),
        #(Permission.objects.get(content_type=ad_type, codename="delete_ad").pk, u'删除广告'),

        (Permission.objects.get(content_type=app_type, codename="add_app").pk, u'添加应用'),
        (Permission.objects.get(content_type=app_type, codename="change_app").pk, u'编辑应用'),
        (Permission.objects.get(content_type=app_type, codename="delete_app").pk, u'删除应用'),
        (Permission.objects.get(content_type=app_type, codename="publish_app").pk, u'上线应用'),
        (Permission.objects.get(content_type=app_type, codename="drop_app").pk, u'下线应用'),
        #(Permission.objects.get(content_type=app_type, codename="audit_app").pk, u'审核应用')

        (Permission.objects.get(content_type=subject_type, codename="add_subject").pk, u'添加应用专题'),
        (Permission.objects.get(content_type=subject_type, codename="change_subject").pk, u'编辑应用专题'),
        (Permission.objects.get(content_type=subject_type, codename="delete_subject").pk, u'删除应用专题'),
        (Permission.objects.get(content_type=subject_type, codename="publish_subject").pk, u'上线应用专题'),
        (Permission.objects.get(content_type=subject_type, codename="drop_subject").pk, u'下线应用专题'),
        (Permission.objects.get(content_type=subject_type, codename="sort_subject").pk, u'调整应用专题顺序'),

        (Permission.objects.get(content_type=log_meta_type, codename='view_organization_statistics').pk, u'查看所在组织统计数据'),
        (Permission.objects.get(content_type=log_entity_type, codename='view_all_data').pk, u'查看所有数据'),
        #(Permission.objects.get(content_type=oplog_type, codename='oplog').pk, u'查看操作日志')
    )
    return _available_permissions


def get_permission_name(permission):
    for p in get_available_permissions():
        if p[0] == permission.pk: return p[1]
    return None

