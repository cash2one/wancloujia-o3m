#coding: utf-8
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.conf import settings

from dajaxice.core import dajaxice_autodiscover, dajaxice_config

from app.views import category, plate_list
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
    url(r'^plates', 'app.views.plates'),
    url(r'^recommends', category('recommends')),
    url(r'^games', category('games')),
    url(r'^gifts', category('gifts')),
    url(r'^onlinegames', category('onlinegames')),
    url(r'^weekrank', category('weekrank')),
    url(r'^gamerank', category('gamerank')),
    url(r'^apprank', category('apprank')),
    url(r'^zone1', category('zone1')),
    url(r'^zone2', category('zone2')),
    url(r'^top1', plate_list('top1')),
    url(r'^top2', plate_list('top2')),
    url(r'^top3', plate_list('top3')),
    url(r'^top4', plate_list('top4')),
    url(r'^top5', plate_list('top5')),
    url(r'^top6', plate_list('top6')),
    url(r'^top7', plate_list('top7')),
    url(r'^top8', plate_list('top8')),
    url(r'^top9', plate_list('top9')),
    url(r'^middle', plate_list('middle')),
    url(r'^bottom1', plate_list('bottom1')),
    url(r'^bottom2', plate_list('bottom2')),
    url(r'^bottom3', plate_list('bottom3')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
