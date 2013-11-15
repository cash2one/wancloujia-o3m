#coding: utf-8
import logging

from django.shortcuts import render, redirect
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage        
from django.utils import simplejson
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query import QuerySet
from django.db.models import Q
from django.views.decorators.http import require_GET, require_POST
from django import forms

from django_tables2.config import RequestConfig

from suning import settings
from app.models import App, UploadApk
from app.forms import AppForm
from app.tables import AppTable
from suning.decorators import active_tab
import apk


logger = logging.getLogger(__name__)

def can_view_app(user):
    return user.is_superuser or \
            user.is_staff or \
            user.has_module_perms('app')


@require_GET
@login_required
@user_passes_test(can_view_app, login_url=settings.PERMISSION_DENIED_URL)
@active_tab("app")
def app(request):
    query_set = App.objects.all().order_by("online", "create_date")
    query = request.GET.get("q", None)
    if query:
        query_set = query_set.filter(Q(name__contains=query) | Q(desc__contains=query))
    table = AppTable(query_set)
    RequestConfig(request, paginate={"per_page": settings.PAGINATION_PAGE_SIZE}).configure(table)
    return render(request, "app.html", {
        "query": query,
        "table": table,
        'form': AppForm()
    });

class UploadForm(forms.ModelForm):
    class Meta:
        model = UploadApk
        fields = ('file',)


@require_POST
@login_required
@user_passes_test(can_view_app, login_url=settings.PERMISSION_DENIED_URL)
def upload(request):
    form = UploadForm(data=request.POST, files=request.FILES)
    if not form.is_valid():
        logger.warn("%s: form is invalid" % __name__)
        logger.warn(form.errors)
        return HttpResponseBadRequest(simplejson.dumps({'errors': form.errors}))

    uploaded_file = form.save()
    apk_info = apk.inspect(uploaded_file.file.path)

    holder = {'icon_url': None}
    def copy_icon(name, f):
        path = "apk_icons/" + apk_info.getPackageName() + "/" + name
        holder['icon_url'] = settings.MEDIA_URL + default_storage.save(path, ImageFile(f))
    apk.read_icon(uploaded_file.file.path, copy_icon)

    return HttpResponse(simplejson.dumps({
        'apk_id': uploaded_file.pk,
        'name': apk_info.getAppName(),
        'packageName': apk_info.getPackageName(),
        'version': apk_info.versionName,
        'size': apk_info.packageSize,
        'icon': holder['icon_url']
    }))

