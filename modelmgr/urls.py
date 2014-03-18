from django.conf.urls import patterns, url

urlpatterns = patterns('modelmgr.views',
    url('^$', 'models'),
    url('^(?P<id>\d+)$', 'model_by_id'),
    url('^query$', 'query'),
)
