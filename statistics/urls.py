from django.conf.urls import patterns, url

urlpatterns = patterns('statistics.views',
    url(r'^flow/$', 'flow'),
)
