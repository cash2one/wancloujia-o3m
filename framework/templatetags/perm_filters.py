#coding: utf-8
import logging

from django import template
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

import mgr.views
import app.views
from mgr.models import Employee, Store, cast_staff
from suning.permissions import *

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter
def is_employee(user):
    return not user.is_staff and not user.is_superuser


@register.filter
def is_not_employee(user):
    return not is_employee(user)


@register.filter
def in_group(user, name):
    groups = Group.objects.filter(name=name)
    return groups[0] in user.groups if len(groups) > 0 else False

@register.filter
def in_store(user):
    return cast_staff(user).in_store()


@register.filter
def can_view_staff(user):
    return mgr.views.can_view_staff(user)


@register.filter
def can_change_company(user):
    if user.is_superuser or user.is_staff:
        return True
    user = cast_staff(user)
    return not user.in_store() and user.has_perm("mgr.change_organization")


@register.filter
def can_view_organization(user):
    return mgr.views.can_view_organization(user)


@register.filter
def can_add_organization(user):
    return mgr.views.can_add_organization(user)


@register.filter
def can_add_store(user):
    return mgr.views.can_add_store(user)


@register.filter
def can_delete_store(user):
    return mgr.views.can_delete_store(user)


@register.filter
def get_permissions(user):
    permissions = user.user_permissions.all()
    return ', '.join([get_permission_name(p) for p in permissions])


@register.filter
def can_view_app(user):
    return suning.views.can_view_app(user)


@register.filter
def can_view_subject(user):    
    return suning.views.can_view_subject(user)
    