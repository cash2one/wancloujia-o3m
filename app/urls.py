from django.conf.urls import patterns, url

urlpatterns = patterns('app.views',
    url('^$', 'app'),
    url('^upload$', 'upload')
)
