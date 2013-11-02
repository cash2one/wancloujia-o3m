from django import template

from mgr import models

register = template.Library()

@register.filter
def get_groups(user):
    return ','.join([str(g.id) for g in user.groups.all()])
    

@register.filter
def is_group_built_in(group):
    return models.is_group_built_in(group)

