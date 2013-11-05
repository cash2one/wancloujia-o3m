import logging

from django import template
from haystack.models import SearchResult

from mgr import models
from mgr.search_indexes import CompanyIndex

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter
def count_stores(company):
    if isinstance(company, SearchResult):
        company = company.object
    return models.Store.objects.filter(company=company).count()
    
@register.filter
def get_organization_id(user):
    return "" if user.is_staff else user.cast().organization.pk

@register.filter
def is_group_built_in(group):
    return models.is_group_built_in(group)

