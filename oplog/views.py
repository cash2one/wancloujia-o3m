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
from mgr.views import user_passes_test
from mgr.models import Staff
from suning.utils import render_json

from mgr.models import Staff
from oplog.forms import OpLogForm
import datetime
from framework.templatetags.perm_filters import can_view_oplog
logger = logging.getLogger(__name__)


@require_GET
@login_required
@user_passes_test(can_view_oplog,login_url=settings.PERMISSION_DENIED_URL)
@active_tab("system", "oplog")
def get_oplog(request):
    form = OpLogForm(request.GET)
    logger.debug(dir(form))
    query_set = op_log.objects.all().order_by("-pk")
    if form.is_valid():
        from_date = form.cleaned_data['from_date'] #datetime.strptime(form.cleaned_data['from_date'],'%Y-%m-%d')
        to_date = form.cleaned_data['to_date'] + datetime.timedelta(days=1)#datetime.strptime(form.cleaned_data['to_date'],'%Y-%m-%d')
        if from_date <= to_date:
            query_set = query_set.filter(date__gte=from_date,date__lt=to_date)
        if form.cleaned_data['username'] != '-1':
            query_set = query_set.filter(username=Staff.objects.get(pk=form.cleaned_data['username']).username)
        if form.cleaned_data['type'] != '-1':
            query_set = query_set.filter(type=form.cleaned_data['type'])

    table = OpLogTable(query_set)
    table.empty_text = settings.NO_SEARCH_RESULTS
    count = query_set.count()
    RequestConfig(request, paginate={"per_page": 50}).configure(table)
    
    return render(request, "oplog.html", {
        'table': table,
        'form': form,
        'f_date': form.cleaned_data['from_date'].strftime('%Y-%m-%d') if form.cleaned_data.has_key('from_date') else datetime.date.today().strftime('%Y-%m-%d'),
        't_date': form.cleaned_data['to_date'].strftime('%Y-%m-%d') if form.cleaned_data.has_key('to_date') else datetime.date.today().strftime('%Y-%m-%d'),
        'count': count if count > 0 else 0,
    })
