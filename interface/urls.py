__author__ = 'bridge'
from django.conf.urls import patterns, url

urlpatterns = patterns('interface.views',
    url(r'^logout$', 'logout'),
    url(r'^data', 'upload'),
    url(r'^echo$', 'echo'),

    url(r'^welcome$', 'welcome'),
    url(r'^subjects$', 'subjects'),
    url(r'^subjects/(?P<id>\d+)$', "apps"),

    url(r'^(?P<addr>/\S+)', 'get_hdfs_file'),
)
