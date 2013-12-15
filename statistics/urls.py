from django.conf.urls import patterns, url

urlpatterns = patterns('statistics.views',
    url(r'^flow$', 'flow'),
    url(r'^flow/excel$', 'flow_excel'),
    url(r'^capacity$', 'capacity'),
    url(r'^capacity/excel$', 'capacity_excel'),
    url(r'^device$', 'device'),
    url(r'^regions$', 'regions'),
    url(r'^companies$', 'companies'),
    url(r'^stores$', 'stores'),
    url(r'^employee$', 'employee'),
    url(r'^apps$', 'apps'),
)
