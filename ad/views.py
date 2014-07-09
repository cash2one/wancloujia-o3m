#coding: utf-8
import logging
from django import forms

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.db.models.query import QuerySet
from django.db.models import Q
from django.views.decorators.http import require_GET, require_POST
from django_tables2.config import RequestConfig
from app.models import Subject

from django.conf import settings
from ad.models import AD
from ad.forms import ADForm
from ad.tables import ADTable
from og.decorators import active_tab

from django_render_json import json as as_json
from django_render_json import render_json


logger = logging.getLogger(__name__)

def can_view_ad(user):
    if user.is_superuser or user.is_staff:
        return True

    return user.has_module_perms('ad')


@require_GET
@login_required
@user_passes_test(can_view_ad, login_url=settings.PERMISSION_DENIED_URL)
@active_tab("ad")
def ad(request):
    table = ADTable(AD.objects.all())
    RequestConfig(request, paginate={"per_page": 5}).configure(table)
    return render(request, "ad.html", {
        "table": table,
        'form': ADForm()
    })


@require_POST
@as_json
def edit_ad(request):
    pk = request.POST.get('pk')
    cover = request.POST.get('cover')
    link = request.POST.get('link');
    AD.objects.filter(pk=pk).update(cover=cover, link=link);
    return {
        'ret_code': 0
    }


def permalink(host, path, scheme='http'):
    return scheme + '://' + host + path


def render_jsonp(data, callback=None):
    if callback is None:
        return render_json(data, indent=4, ensure_ascii=False)

    import json
    content = callback + '(' + json.dumps(data, indent=4, ensure_ascii=False) + ')'
    return HttpResponse(content, content_type='text/plain')


def ads(request):
    host = request.META['HTTP_HOST']
    ads = AD.objects.all().order_by('pk');
    main = ads[0]
    side = ads[1]

    return render_jsonp({
        "main": {
            "cover": permalink(host, main.cover or '/static/img/main_ad.png'),
            "url": main.link
        },
        "side": {
            "cover": permalink(host, side.cover or '/static/img/side_ad.png'),
            "url": side.link
        }
    }, request.GET.get('callback'))

