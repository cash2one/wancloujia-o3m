import logging

from django import template
from haystack.models import SearchResult

from mgr.models import Store, Company
from mgr.search_indexes import CompanyIndex

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter
def count_stores(company):
    if isinstance(company, SearchResult):
        company = company.object
    return Store.objects.filter(company=company).count()
    
@register.filter
def get_organization_id(user):
    return "" if user.is_staff else user.cast().organization.pk

