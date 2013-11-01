import logging
from django import template

logger = logging.getLogger(__name__)
register = template.Library()

def min(a, b):
    return a if a < b else b


def max(a, b):
    return a if a > b else b

@register.filter
def get_pages(table):
    current = table.page.number
    total = table.paginator.num_pages
    logger.debug("current: %d, total: %d" % (current, total))
    offset = max(1, current-5)
    length = min(10, total-offset+1)
    logger.debug("offset: %d, length: %d" % (offset, length))
    return range(offset, offset + length)

