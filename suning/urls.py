from django.conf.urls import patterns, include, url

from dajaxice.core import dajaxice_autodiscover, dajaxice_config

dajaxice_autodiscover()

urlpatterns = patterns('',
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^select2/', include('django_select2.urls')),
    url(r'', include('framework.urls')),
    #url(r'^app/', include('app.urls')),
    url(r'^mgr/', include('mgr.urls')),
    url(r'ad/', include('ad.urls')),
)
