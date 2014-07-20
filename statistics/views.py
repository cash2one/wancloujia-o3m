#coding: utf-8
import logging
import datetime
import math
import HTMLParser 

from django.db.models import Q

from django import forms
from django.utils import simplejson
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query import QuerySet
from django.db.models import Q, Sum, Count
from django.views.decorators.http import require_GET, require_POST
from django_tables2.config import RequestConfig
from django.http import HttpResponse, Http404

from og.decorators import active_tab
from app.models import App
from forms import DownloadFilterForm

from og.utils import render_json

logger = logging.getLogger(__name__)


@active_tab("statistics", "download")
def download(request):
    return render(request, "download.html", {
        'filter': DownloadFilterForm()
        })


@require_GET
def apps(request):
    if not request.user.is_authenticated():
        return render_json({'more': False, 'results': []})
    q = request.GET.get('q', "")
    p = request.GET.get('p', "")
    page = int(p) if p else 0

    APPS_PER_PAGE = 10
    apps = App.objects.filter(Q(name__contains=q) | Q(package__contains=q))
    total = len(apps)
    apps = apps[(page-1)*APPS_PER_PAGE:page*APPS_PER_PAGE]
    results = map(lambda e: {'id': e.pk, 'text': e.name}, apps)

    return render_json({'more': total > page * APPS_PER_PAGE, 'results': results})


