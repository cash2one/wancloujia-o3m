#coding: utf-8
import logging

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from suning.decorators import active_tab
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

from django_tables2.config import RequestConfig
from feedback.models import Feedback, HandledFeedback
from django.db.models import Q
from suning import settings
from feedback.tables import FeedbackTable, HandledFeedbackTable


logger = logging.getLogger(__name__)


def get_oplog(request):
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