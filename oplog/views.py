#coding: utf-8
import logging

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from og.decorators import active_tab
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
from django.core.context_processors import csrf

logger = logging.getLogger(__name__)


@login_required
@user_passes_test(can_view_oplog, login_url=settings.PERMISSION_DENIED_URL)
@active_tab("system", "oplog")
def get_oplog(request):
    form = OpLogForm(request.POST)
    logs = op_log.objects.all().order_by('-pk')
    from_date = datetime.date.today() + datetime.timedelta(days=-6)
    to_date = datetime.date.today()
    if form.is_valid():
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date'] + datetime.timedelta(days=1)
        if from_date <= to_date:
            logs = logs.filter(date__gte=from_date, date__lt=to_date)
        if int(form.cleaned_data['username']) != -1:
            logs = logs.filter(username=Staff.objects.get(pk=int(form.cleaned_data['username'])).username)
        if int(form.cleaned_data['type']) != -1:
            logs = logs.filter(type=int(form.cleaned_data['type']))
        to_date = to_date + datetime.timedelta(days=-1)
    table = OpLogTable(logs)
    count = logs.count()
    RequestConfig(request, paginate={"per_page": 50}).configure(table)
    f_date = from_date.strftime('%Y-%m-%d')
    t_date = to_date.strftime('%Y-%m-%d')
    return render(request, "oplog.html", {
        'table': table,
        'form': form,
        'f_date': f_date,
        't_date': t_date,
        'count': count if count > 0 else 0,
    })
