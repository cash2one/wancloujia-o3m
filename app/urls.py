from django.conf.urls import patterns, url

urlpatterns = patterns('app.views',
    url('^$', 'apps'),
    url('^add$', 'editApp'),
    url('^edit$', 'editApp'),
    url('^delete$', 'deleteApp'),
    url('^subject/$', 'subject'),
    url('^subject/edit$', 'add_edit_subject'),
    url('^plate/$', 'plate'),
    url('^plate/edit$', 'add_edit_plate'),
    url('^search_apps/$', 'search_apps'),
    url('^upload$', 'upload')
)
