#coding: utf-8
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic.base import RedirectView 
from django.conf import settings

from dajaxice.core import dajaxice_autodiscover, dajaxice_config

from app.views import category
dajaxice_autodiscover()

urlpatterns = patterns('',
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
    url(r'^ajax-upload/', include('ajax_upload.urls')),
    url(r'^select2/', include('django_select2.urls')),
    url(r'', include('framework.urls')),
    url(r'^app/', include('app.urls')),
    url(r'^statistics/', include('statistics.urls')),
    url(r'^mgr/', include('mgr.urls')),
    url(r'muce/', include('interface.purls')),
    url(r'interface/', include('interface.urls')),
    url(r'^ad/', include('ad.urls')),

    url(r'^apps/(?P<package>.+)', 'app.views.app'),
    url(r'^ads', 'ad.views.ads'),
    url(r'^recommends', category('recommends')),
    url(r'^games', category('games')),
    url(r'^gifts', category('gifts')),
    url(r'^onlinegames', category('onlinegames')),
    url(r'^weekrank', category('weekrank')),
    url(r'^gamerank', category('gamerank')),
    url(r'^apprank', category('apprank')),
    url(r'^zone1', category('zone1')),
    url(r'^zone2', category('zone2')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
