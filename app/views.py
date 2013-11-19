#coding: utf-8
import logging
from itertools import chain

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
    published_apps = App.objects.filter(online=True).order_by("-create_date")
    droped_apps = App.objects.filter(online=False).order_by("-create_date")
    query = request.GET.get("q", None)
    if query:
        published_apps = published_apps.filter(Q(name__contains=query) | Q(desc__contains=query))
        droped_apps = droped_apps.filter(Q(name__contains=query) | Q(desc__contains=query))

    query_set = list(chain(published_apps, droped_apps))
    table = AppTable(query_set)
    if query:
        table.empty_text = u'无搜索结果'
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
@login_required(login_url=settings.LOGIN_JSON_URL)
def upload(request):
    form = UploadForm(data=request.POST, files=request.FILES)
    if not form.is_valid():
        logger.warn("%s: form is invalid" % __name__)
        logger.warn(form.errors)
        return HttpResponseBadRequest(simplejson.dumps({'errors': form.errors}))

    uploaded_file = form.save()

    try:
        apk_info = apk.inspect(uploaded_file.file.path)
    except Exception as e:
        logger.exception(e)
        return HttpResponse(simplejson.dumps({
            'ret_code': 1000,
            'ret_msg': 'inspect_apk_failed'
        }), mimetype='application/json')

    holder = {'icon_url': None}
    def copy_icon(name, f):
        path = "apk_icons/" + apk_info.getPackageName() + "/" + name
        holder['icon_url'] = settings.MEDIA_URL + default_storage.save(path, ImageFile(f))
    apk.read_icon(uploaded_file.file.path, copy_icon)
    app_dict = {
        'apk_id': uploaded_file.pk,
        'name': apk_info.getAppName(),
        'packageName': apk_info.getPackageName(),
        'version': apk_info.versionName,
        'size': apk_info.packageSize,
        'icon': holder['icon_url']
    }

    apps = App.objects.filter(package=apk_info.getPackageName())
    if len(apps) > 0:
        app = apps[0]
        app_dict["id"] = app.pk
        app_dict["category"] = app.category.pk
        app_dict["desc"] = app.desc
        app_dict["popularize"] = "True" if app.popularize else "False"

    return HttpResponse(simplejson.dumps(app_dict), 
                        mimetype='application/json')
