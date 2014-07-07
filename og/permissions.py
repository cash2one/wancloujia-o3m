#coding: utf-8
from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from mgr.models import Organization, Staff
from ad.models import AD
from app.models import App, Subject


_available_permissions = None


def get_available_permissions():
        return ()


def get_permission_name(permission):
    for p in get_available_permissions():
        if p[0] == permission.pk: return p[1]
    return None

