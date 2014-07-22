__author__ = 'bridge'
from django.conf.urls import patterns, url

urlpatterns = patterns('interface.views',
    url(r'^logout$', 'logout'),
    url(r'^data', 'upload'),
    url(r'^signal', 'signal'),
    url(r'^echo$', 'echo'),

    url(r'^welcome$', 'welcome'),

    url(r'^subjects/(?P<id>\d+)$', "apps"),
    url(r'^subjects', 'subjects'),
    #url(r'^(?P<addr>/\S+)', 'get_hdfs_file'),
    url(r'^feedback', 'feedback'),
    url(r'^add_download_log$', 'add_download'),
    url(r'^download', "download")
)
