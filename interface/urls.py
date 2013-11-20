__author__ = 'bridge'
from django.conf.urls import patterns, url

urlpatterns = patterns('interface.views',
    url('^login/(?P<username>[^/]+)/(?P<password>[^/]+)$', 'user_login'),
    url('^logout$', 'user_logout'),
    url('^upload$', 'upload'),
    url('^subject_apps$', 'subject_apps'),
    url('^subjects', 'all_subjects'),
    url('^create_subject', 'create_subject'),
    url(r'^echo$', 'echo'),
)
