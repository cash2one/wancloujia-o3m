__author__ = 'bridge'
from django.conf.urls import patterns, url

urlpatterns = patterns('interface.views',
    url(r'^login/(?P<username>[^/]+)/(?P<password>[^/]+)$', 'user_login'),
    url(r'^logout$', 'user_logout'),
    url(r'^upload$', 'upload'),
    url(r'^echo$', 'echo'),

    url(r'^welcome$', 'welcome'),
    url(r'^subjects$', 'subjects'),
    url(r'^subjects/(?P<id>\d+)$', "apps"),
)