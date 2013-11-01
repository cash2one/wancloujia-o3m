from django.conf.urls import patterns, url

urlpatterns = patterns('mgr.views',
    url(r'^account$', 'account'),
    url(r'^organization/$', 'organization'),
    url(r'^user$', 'user')
)
