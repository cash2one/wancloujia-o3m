import logging
from django import template

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag()
def qs_attr(queryset, attr, sep=","):
    return sep.join([unicode(getattr(item, attr)) for item in queryset])

