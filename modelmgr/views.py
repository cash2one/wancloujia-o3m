import logging
from django import forms

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query import QuerySet
from django.db.models import Q
from django.views.decorators.http import require_GET
from django_tables2.config import RequestConfig
from models import Model
from tables import ModelTable
from forms import ModelForm

from suning import settings
from suning.decorators import active_tab

logger = logging.getLogger(__name__)


def can_view_models(user):
    if user.is_superuser or user.is_staff:
        return True

    return user.has_model_perms('modelmgr');


@require_GET
@login_required
@user_passes_test(can_view_models, login_url=settings.PERMISSION_DENIED_URL)
@active_tab("modelmgr")
def models(request):
    query_set = Model.objects.all().order_by("-pk")
    query = request.GET.get("q", None)

    if query:
        query_set = query_set.filter(Q(name__contains=query) | Q(ua__contains=query))

    form = ModelForm()
    table = ModelTable(query_set)
    RequestConfig(request, paginate={"per_page": 10}).configure(table);
    return render(request, "model.html", {
        "query": query,
        "form": form,
        "table": table
    })
