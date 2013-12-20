from django.conf.urls import patterns, url

urlpatterns = patterns('feedback.views',
    url(r'^handled/', 'handled_feedback'),
    url(r'^$', 'feedback'),
)
