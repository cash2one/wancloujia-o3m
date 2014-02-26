#coding: utf-8
from django.db.models.signals import post_syncdb
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from mgr.models import Organization, Staff, get_built_in_group_names
from ad.models import AD
from app.models import App, Subject
from interface.models import LogMeta


def _ensure_built_in_groups():
    for group_name in get_built_in_group_names():
        if not Group.objects.filter(name=group_name).exists():
            Group(name=group_name).save()


def _ensure_permissions_for_built_in_groups():
    organization_type = ContentType.objects.get_for_model(Organization)
    staff_type = ContentType.objects.get_for_model(Staff)
    ad_type = ContentType.objects.get_for_model(AD)
    app_type = ContentType.objects.get_for_model(App)
    subject_type = ContentType.objects.get_for_model(Subject)
    log_meta_type = ContentType.objects.get_for_model(LogMeta)

    group = Group.objects.get(name=u'管理组') 
    group.permissions = [
        Permission.objects.get(content_type=organization_type, codename='add_organization'), 
        Permission.objects.get(content_type=organization_type, codename='change_organization'), 
        Permission.objects.get(content_type=staff_type, codename="add_staff"),
        Permission.objects.get(content_type=staff_type, codename="change_staff"),
        Permission.objects.get(content_type=log_meta_type, 
                               codename='view_organization_statistics')
    ]
    group.save()
    '''
    group = Group.objects.get(name=u'广告组')
    group.permissions = [
        Permission.objects.get(content_type=ad_type, codename='add_ad'), 
        Permission.objects.get(content_type=ad_type, codename='change_ad'), 
        Permission.objects.get(content_type=ad_type, codename="delete_ad"),
        Permission.objects.get(content_type=ad_type, codename="sort_ad"),
    ]
    group.save()
    '''
    group = Group.objects.get(name=u'应用组')
    group.permissions = [
        Permission.objects.get(content_type=app_type, codename='add_app'), 
        Permission.objects.get(content_type=app_type, codename='change_app'), 
        Permission.objects.get(content_type=app_type, codename="delete_app"),
        Permission.objects.get(content_type=app_type, codename="publish_app"),
        Permission.objects.get(content_type=app_type, codename="drop_app"),
        Permission.objects.get(content_type=subject_type, codename='add_subject'), 
        Permission.objects.get(content_type=subject_type, codename='change_subject'), 
        Permission.objects.get(content_type=subject_type, codename="delete_subject"),
        Permission.objects.get(content_type=subject_type, codename="publish_subject"),
        Permission.objects.get(content_type=subject_type, codename="drop_subject"),
        Permission.objects.get(content_type=subject_type, codename="sort_subject")
    ]
    group.save()


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        _ensure_built_in_groups()
        _ensure_permissions_for_built_in_groups()

