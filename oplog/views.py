#coding: utf-8
import logging

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from suning.decorators import active_tab
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

from django_tables2.config import RequestConfig
from oplog.models import op_log
from django.db.models import Q
from suning import settings
from oplog.tables import OpLogTable
from mgr.views import user_passes_test, can_view_staff
from suning.utils import render_json

from oplog.models import OPLOG_TYPE_CHOICE
logger = logging.getLogger(__name__)


@require_GET
@login_required
@user_passes_test(can_view_staff, login_url=settings.PERMISSION_DENIED_URL)
@active_tab("system", "oplog")
def get_oplog(request):
    query_set = op_log.objects.all().order_by("-pk")
    query = request.GET.get("q", None)
    if query:
        query_set = query_set.filter(Q(content__contains=query))
    table = OpLogTable(query_set)
    if query:
        table.empty_text = settings.NO_SEARCH_RESULTS
    count = len(op_log.objects.all())
    RequestConfig(request, paginate={"per_page": settings.PAGINATION_PAGE_SIZE}).configure(table)
    return render(request, "oplog.html", {
        'query': query,
        'table': table,
        'count': count if count > 0 else None
    })

@require_GET
def track_type(request):
    user = request.user
    if not user.is_authenticated():
        regions = Region.objects.none()

    dict = {}
    for id, type in OPLOG_TYPE_CHOICE:
        dict[id] = type
    return render_json(dict)

@require_GET
def users(request):
    pass


@require_GET
@login_required
@active_tab("feedback")
def feedback(request):
    query_set = Feedback.objects.all().order_by("-pk")
    query = request.GET.get("q", None)
    if query:
        query_set = query_set.filter(Q(content__contains=query))
    table = FeedbackTable(query_set)
    if query:
        table.empty_text = settings.NO_SEARCH_RESULTS
    count = len(Feedback.objects.all())
    RequestConfig(request, paginate={"per_page": settings.PAGINATION_PAGE_SIZE}).configure(table)
    return render(request, "oplog.html", {
        'query': query,
        'table': table,
        'count': count if count > 0 else None
    })
