from django.conf.urls import patterns, url

urlpatterns = patterns('statistics.views',
    url(r'^$', 'download'),
    url(r'^download$', 'download'),
    url(r'^ad$', 'ad'),
    url(r'^apps$', 'apps'),
    url(r'^ad_log$', 'ad_log'),
)
