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
from forms import DownloadFilterForm, AdFilterForm

from interface.models import AdsLogEntity
from forms import AdFilterForm

from og.utils import render_json

from dajaxice.utils import deserialize_form

logger = logging.getLogger(__name__)


@active_tab("statistics", "download")
def download(request):
    return render(request, "download.html", {
        'filter': DownloadFilterForm()
        })

@active_tab("statistics", "ad")
def ad(request):
    return render(request, "sta_ad.html", {
        'filter': AdFilterForm()
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

    
def ad_log(request):
    form = deserialize_form(request.GET['f'])
    filter_form = AdFilterForm(form)
    if not filter_form.is_valid():
        logger.warn("form is not valid")
        return _invalid_data_json

    from_date = filter_form.cleaned_data['from_date']
    to_date = filter_form.cleaned_data['to_date']
    to_datetime = datetime.datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59) 

    logs = AdsLogEntity.objects.all()
    logs = logs.filter(datetime__gte=from_date)
    logs = logs.filter(datetime__lte=to_datetime)
    
    resp = {}
    resp['main'] = {'view':{}, 'click':{}}
    resp['side'] = {'view':{}, 'click':{}}
    tmp_date = from_date
    while True:
        if tmp_date > to_date:
            break
        tmp_str = tmp_date.strftime("%Y-%m-%d")
        resp['main']['view'][tmp_str] = 0
        resp['side']['view'][tmp_str] = 0
        resp['main']['click'][tmp_str] = 0
        resp['side']['click'][tmp_str] = 0
        tmp_date += datetime.timedelta(days=1)
    main_view = 0
    main_click = 0
    side_view = 0
    side_click = 0
    for log in logs:
        date_str = log.datetime.strftime("%Y-%m-%d")
        if log.adTitle == u"主广告位":
            resp['main'][log.op][date_str] += 1
            if log.op == 'view':
                main_view += 1
            else:
                main_click += 1
        else:
            resp['side'][log.op][date_str] += 1
            if log.op == 'view':
                side_view += 1
            else:
                side_click += 1

            
    return render_json({
        'ret_code': 0,
        'logs': resp,
        'main_view': main_view,
        'main_click': main_click,
        'side_view': side_view,
        'side_click': side_click
        })

