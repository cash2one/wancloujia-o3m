#coding: utf-8
import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query import QuerySet
from django.db.models import Q
from django.views.decorators.http import require_GET
from django_tables2.config import RequestConfig

from suning import settings
from ad.models import AD
from ad.forms import ADForm
from ad.tables import ADTable
from suning.decorators import active_tab

def can_view_ad(user):
    if user.is_superuser or user.is_staff:
        return True

    return user.has_perm('ad.add_ad') or \
            user.has_perm('ad.change_ad') or \
            user.has_perm('ad.delete_ad')


@require_GET
@login_required
@user_passes_test(can_view_ad, login_url=settings.PERMISSION_DENIED_URL)
@active_tab("ad")
def ad(request):
    table = ADTable(AD.objects.all())
    RequestConfig(request, paginate={"per_page": settings.PAGINATION_PAGE_SIZE}).configure(table)
    return render(request, "ad.html", {
        "table": table,
        'form': ADForm()
    });

