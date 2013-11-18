__author__ = 'bridge'
from django.conf.urls import patterns, url

urlpatterns = patterns('interface.views',
    url('^login/(?P<username>[^/]+)/(?P<password>[^/]+)$', 'user_login'),
    url('^logout$', 'user_logout'),
    url('^upload$', 'upload'),
)
