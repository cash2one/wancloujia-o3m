#coding: utf-8
import math
import logging
from itertools import chain

from django.shortcuts import render, redirect
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

from suning import settings
from app.models import App, UploadApk, Subject
from app.forms import AppForm, SubjectForm
from app.tables import AppTable, SubjectTable
from suning.decorators import active_tab
from interface.storage import hdfs_storage
import apk
import os

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
        table.empty_text = settings.NO_SEARCH_RESULTS
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
    #raise Http404;
    form = UploadForm(data=request.POST, files=request.FILES)
    if not form.is_valid():
        logger.warn("%s: form is invalid" % __name__)
        logger.warn(form.errors)
        return Http404

    uploaded_file = form.save()

    try:
        apk_info = apk.inspect(uploaded_file.file.path)
        dfs = hdfs_storage()
        dfs.create(uploaded_file.file.path, uploaded_file.file.path)
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
        dfs.create(key_path, key_path)
    apk.read_icon(uploaded_file.file.path, copy_icon)
    app_dict = {
        'ret_code': 0,
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
    query_set = Subject.objects.order_by("position", "-create_date")
    #published_subjects = Subject.objects.filter(online=True).order_by("-create_date")
    #droped_subjects = Subject.objects.filter(online=False).order_by("-create_date")
    query = request.GET.get("q", None)
    if query:
        #published_subjects = published_subjects.filter(Q(name__contains=query) | Q(desc__contains=query))
        #droped_subjects = droped_subjects.filter(Q(name__contains=query) | Q(desc__contains=query))
        query_set = query_set.filter(Q(name__contains=query) | Q(desc__contains=query))

    #query_set = list(chain(published_subjects, droped_subjects))
    table = SubjectTable(query_set)
    if query:
        table.empty_text = settings.NO_SEARCH_RESULTS
    RequestConfig(request, paginate={"per_page": settings.PAGINATION_PAGE_SIZE}).configure(table)

    subjects = Subject.objects.filter(online=True).order_by("position")
    subject_list = [{"id": subject.pk, "name": subject.name} for subject in subjects]
    
    return render(request, "subject.html", {
        "subject_list": subject_list,
        "query": query,
        "table": table,
        'form': SubjectForm()
    })


@require_GET
@login_required(login_url=settings.LOGIN_JSON_URL)
def search_apps(request):
    query = request.GET.get("q", "")
    page = int(request.GET.get("p"))
    page_limit = int(request.GET.get("page_limit"))

    apps = App.objects.filter(online=True).filter(name__contains=query)
    total = apps.count()
    apps = apps[(page-1)*page_limit:page*page_limit]
    results = [{'id': app.pk, 'text': app.name} for app in apps]

    json = simplejson.dumps({
        'ret_code': 0, 
        'results': results, 
        'total': total
    })
    return HttpResponse(json, mimetype='application/json')
