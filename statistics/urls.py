from django.conf.urls import patterns, url

urlpatterns = patterns('statistics.views',
    url(r'^flow$', 'flow'),
    url(r'^flow/excel$', 'flow_excel'),
    url(r'^capacity$', 'capacity'),
    url(r'^capacity/excel$', 'capacity_excel'),
    url(r'^device$', 'device'),
    url(r'^device/excel$', 'device_excel'),
    url(r'^organization$', 'organization'),
    url(r'^organization/(?P<mode>[a-z]+)_(?P<level>[a-z]+)/excel$', 'organization_excel'),

    # query
    url(r'^regions$', 'regions'),
    url(r'^companies$', 'companies'),
    url(r'^stores$', 'stores'),
    url(r'^employee$', 'employee'),
    url(r'^apps$', 'apps'),
    url(r'^brands$', 'brands'),
    url(r'^models$', 'models'),
    url(r'^devices$', 'devices'),
    url(r'^subjects$', 'subjects'),
    url(r'^users$', 'users')
)
