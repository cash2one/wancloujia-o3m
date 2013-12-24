#coding: utf-8
import logging
from django import forms

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query import QuerySet
from django.db.models import Q
from django.views.decorators.http import require_GET
from django_tables2.config import RequestConfig
from app.models import Subject

from suning import settings
from ad.models import AD
from ad.forms import ADForm
from ad.tables import ADTable
from suning.decorators import active_tab


def can_view_ad(user):
    if user.is_superuser or user.is_staff:
        return True

    return user.has_module_perms('ad')


@require_GET
@login_required
@user_passes_test(can_view_ad, login_url=settings.PERMISSION_DENIED_URL)
@active_tab("ad")
def ad(request):
    query_set = AD.objects.all().order_by("position")
    query = request.GET.get("q", None)
    if query:
        query_set = query_set.filter(Q(title__contains=query) | Q(desc__contains=query))
    table = ADTable(query_set)
    RequestConfig(request, paginate={"per_page": 5}).configure(table)
    visible_ads = AD.objects.filter(visible=True).order_by("position")
    ad_list = [{"id": ad.pk, "title": ad.title} for ad in visible_ads]
    return render(request, "ad.html", {
        "ad_list": ad_list,
        "query": query,
        "table": table,
        'form': ADForm()
    })

