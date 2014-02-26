#coding: utf-8
import logging

from django import template

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter
def render(widget, name):
	return widget.render(name, "")
