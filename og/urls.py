#coding: utf-8
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic.base import RedirectView 
from django.conf import settings

urlpatterns = patterns('',
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
    url(r'^ajax-upload/', include('ajax_upload.urls')),
    url(r'^select2/', include('django_select2.urls')),
    url(r'', include('framework.urls')),
    url(r'^app/', include('app.urls')),
    url(r'^mgr/', include('mgr.urls')),
    url(r'ad/', include('ad.urls')),
    url(r'interface/', include('interface.urls')),
    url(r'oplog/', include('oplog.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
