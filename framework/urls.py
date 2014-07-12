from django.conf.urls import patterns, url

urlpatterns = patterns('framework.views',
    url(r'^welcome$', 'welcome'),
    url(r'^$', 'welcome'),
    url(r'^logout$', 'logout'),
    url(r'^login$', 'login')
)
