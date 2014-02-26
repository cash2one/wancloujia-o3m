import logging

from django import template

from mgr import models

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter
def count_stores(company):
    return models.Store.objects.filter(company=company).count()
    
@register.filter
def get_organization_id(user):
    return "" if user.is_staff else user.cast().organization.pk

@register.filter
def is_group_built_in(group):
    return models.is_group_built_in(group)

