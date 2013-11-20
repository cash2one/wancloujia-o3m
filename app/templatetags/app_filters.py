#coding: utf-8
import logging

from django import template
from app.models import App, AppGroup, Subject


logger = logging.getLogger(__name__)
register = template.Library()


@register.filter
def get_apps(subject):
    appgrps = AppGroup.objects.filter(subject=subject).all().order_by('position')
    return ",".join([str(item.app.pk) for item in appgrps])
