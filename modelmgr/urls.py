from django.conf.urls import patterns, url

urlpatterns = patterns('modelmgr.views',
    url('^$', 'models'),
)
