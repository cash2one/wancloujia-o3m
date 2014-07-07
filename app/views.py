#coding: utf-8
import math
import logging
from itertools import chain
from hashlib import md5
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage        
from django.utils import simplejson
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query import QuerySet
from django.db.models import Q
from django.views.decorators.http import require_GET, require_POST
from django import forms

from django_tables2.config import RequestConfig

from app.models import App, UploadApk, Subject
from app.forms import AppForm, SubjectForm
from app.tables import AppTable, SubjectTable
from og.decorators import active_tab
from django_render_json import json as as_json

import apk
import os

def _file_md5(path):
     with open(path, 'rb') as f:
         m = md5()
         m.update(f.read())
         return m.hexdigest()

logger = logging.getLogger(__name__)

def can_view_app(user):
    return user.is_superuser or \
            user.is_staff or \
            user.has_perm('app.add_app') or \
            user.has_perm('app.change_app') or \
            user.has_perm('app.delete_app') or \
            user.has_perm('app.publish_app') or \
            user.has_perm('app.drop_app')


@require_GET
@login_required
@active_tab("app")
def app(request):
    apps = App.objects.all().order_by("-create_date")
    query = request.GET.get("q", None)
    if query:
        apps = apps.filter(Q(name__contains=query) | Q(desc__contains=query))

    query_set = apps
    table = AppTable(query_set)
    if query:
        table.empty_text = settings.NO_SEARCH_RESULTS
    RequestConfig(request, paginate={"per_page": settings.PAGINATION_PAGE_SIZE}).configure(table)
    return render(request, "app.html", {
        "query": query,
        "table": table,
        'form': AppForm()
    });


@login_required
@active_tab("app")
def editApp(request):
    id = request.GET.get("id", None);
    app = None
    if id:
        apps = App.objects.filter(pk=id)
        app = apps[0] if apps.exists() else None

    if request.method == 'GET':
        if not app:
            form = AppForm()
        else:
            size = app.size()
            form = AppForm(initial={
                "size": size
            }, instance=app)

        return render(request, "edit_app.html", {
            "form": form
        });
    else:
        if app:
            form = AppForm(request.POST, instance=app)
        else:
            form = AppForm(request.POST)

        if not form.is_valid():
            logger.warn("form is invalid")
            logger.warn(form.errors)
            return render(request, "edit_app.html", {
                "form": form 
            });
            
        form.save()
        return redirect("/app");


@login_required
@active_tab("app")
def deleteApp(request):
    id = request.GET.get("id", -1);
    App.objects.filter(pk=id).delete();
    return redirect("/app");


class UploadForm(forms.ModelForm):
    class Meta:
        model = UploadApk
        fields = ('file',)


def _file_md5(path):
    with open(path, 'rb') as f:
        m = md5()
        m.update(f.read())
        return m.hexdigest()


@require_POST
@login_required(login_url=settings.LOGIN_JSON_URL)
def upload(request):
    #import time
    #time.sleep(10)
    #raise Http404;
    form = UploadForm(data=request.POST, files=request.FILES)
    if not form.is_valid():
        logger.warn("%s: form is invalid" % __name__)
        logger.warn(form.errors)
        return Http404
    uploaded_file = form.save()
    logger.debug("save file");
    uploaded_file.md5 = _file_md5(uploaded_file.file.path)
    logger.debug("md5");
    uploaded_file.save();
    logger.debug("save md5");
    
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
        sub_path = default_storage.save(path, ImageFile(f))
        key_path = settings.MEDIA_ROOT + "/" + sub_path
        holder['icon_url'] = settings.MEDIA_URL + sub_path
    apk.read_icon(uploaded_file.file.path, copy_icon)
    app_dict = {
        'ret_code': 0,
        'apk_id': uploaded_file.pk,
        'name': apk_info.getAppName(),
        'packageName': apk_info.getPackageName(),
        'version': apk_info.versionName,
		'versionCode': apk_info.versionCode or 0,
        'size': apk_info.packageSize,
        'icon': holder['icon_url']
    }

    apps = App.objects.filter(package=apk_info.getPackageName())
    if len(apps) > 0:
        app = apps[0]
        app_dict["id"] = app.pk
        app_dict["desc"] = app.desc
        app_dict["oldVersionCode"] = app.version_code
        app_dict["oldVersion"] = app.version
	
    return HttpResponse(simplejson.dumps(app_dict), 
                        mimetype='application/json')


def can_view_subject(user):
    return user.is_superuser or \
            user.is_staff or \
            user.has_perm('app.add_subject') or \
            user.has_perm('app.change_subject') or \
            user.has_perm('app.delete_subject') or \
            user.has_perm('app.publish_subject') or \
            user.has_perm('app.drop_subject') or \
            user.has_perm('app.sort_subject') 


@require_GET
@login_required
@user_passes_test(can_view_subject, login_url=settings.PERMISSION_DENIED_URL)
@active_tab("subject")
def subject(request):
    query_set = Subject.objects.order_by()
    table = SubjectTable(query_set)
    RequestConfig(request, paginate={"per_page": settings.PAGINATION_PAGE_SIZE}).configure(table)
    return render(request, "subject.html", {
        "table": table,
        'form': SubjectForm()
    })


@require_GET
@as_json
def search_apps(request):
    query = request.GET.get("q", "")
    page = int(request.GET.get("p"))
    page_limit = int(request.GET.get("page_limit"))

    apps = App.objects.filter(online=True).filter(name__contains=query)
    total = apps.count()
    apps = apps[(page-1)*page_limit:page*page_limit]
    results = [{'id': app.pk, 'text': app.name} for app in apps]

    return {
        'ret_code': 0, 
        'results': results, 
        'total': total
    }


@require_POST
@as_json
def add_edit_subject(request, form):
    pk = request.POST["id"]
    apps = request.POST["apps"]

    if not apps:
        logger("%s: param is invalid", __name__)
        return _invalid_data_json

    apps = [int(item) for item in form["apps"].split(",")]
    subject = Subject.objects.get(pk=int(pk))
    models.edit_subject(subject, apps, request.user)

    return {'ret_code': 0}
