from django.conf.urls import patterns, url

urlpatterns = patterns('ad.views',  
    url('^$', 'ad'),        
    url('^edit$', 'edit_ad'),        
)

