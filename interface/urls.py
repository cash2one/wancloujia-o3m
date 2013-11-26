__author__ = 'bridge'
from django.conf.urls import patterns, url

urlpatterns = patterns('interface.views',
    url(r'^login$', 'login'),
    url(r'^logout$', 'logout'),
    url(r'^upload$', 'upload'),
    url(r'^echo$', 'echo'),

    url(r'^welcome$', 'welcome'),
    url(r'^subjects$', 'subjects'),
    url(r'^subjects/(?P<id>\d+)$', "apps"),
)
