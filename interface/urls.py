__author__ = 'bridge'
from django.conf.urls import patterns, url

urlpatterns = patterns('interface.views',
    url(r'^login/(?P<username>[^/]+)/(?P<password>[^/]+)$', 'user_login'),
    url(r'^logout$', 'user_logout'),
    url(r'^upload$', 'upload'),
    url(r'^subject_apps$', 'subject_apps'),
    url(r'^subjects', 'all_subjects'),
    url(r'^wandoujia/subjects/(?P<id>\d+)$', "wandoujia_apps"),
    url(r'^wandoujia/subjects$', "wandoujia_subjects"),
    url(r'^echo$', 'echo'),
)
