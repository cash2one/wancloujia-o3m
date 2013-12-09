from django.conf.urls import patterns, url

urlpatterns = patterns('statistics.views',
    url(r'^flow$', 'flow'),
    url(r'^regions$', 'regions'),
    url(r'^companies$', 'companies'),
    url(r'^stores$', 'stores'),
    url(r'^employee$', 'employee'),
)
