from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from haystack.views import SearchView
from haystack.forms import SearchForm

urlpatterns = patterns('ad.views',
    url(r'^search$', login_required(SearchView(
        template='ad_search.html',
        form_class=SearchForm
    )), name='ad_search'),
)

