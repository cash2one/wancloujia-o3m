from django.conf.urls import patterns, url, include

urlpatterns = patterns('mgr.views',
    url(r'^account/$', 'account'),
    url(r'^organization/$', 'organization'),
    url(r'^appearance/$', 'appearance'),
    url(r'^group/$', 'group'),
    url(r'^user/$', 'user'),
)
