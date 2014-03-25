__author__ = 'bridge'
from django.conf.urls import patterns, url

urlpatterns = patterns('interface.views',
    url(r'^data', 'upload'),
    url(r'^signal', 'signal'),
)
