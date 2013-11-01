from django import template
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from mgr.models import Employee

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

