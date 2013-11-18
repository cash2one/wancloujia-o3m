#coding: utf-8
import logging

from models import App, AppGroup, Subject


logger = logging.getLogger(__name__)
register = template.Library()


@register.filter
def get_apps(subject):
    appgrps = AppGroup.objects.filter(subject=subject).all()
    return ",".join([item.app.pk for item in appgrps])
