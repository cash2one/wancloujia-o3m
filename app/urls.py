from django.conf.urls import patterns, url

urlpatterns = patterns('app.views',
    url('^$', 'app'),
    url('^add$', 'editApp'),
    url('^edit$', 'editApp'),
    url('^delete$', 'deleteApp'),
    url('^subject/$', 'subject'),
    url('^search_apps/$', 'search_apps'),
    url('^upload$', 'upload')
)
