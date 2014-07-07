#coding: utf-8
import math
from datetime import datetime
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
from django.forms.models import model_to_dict

from django_tables2.config import RequestConfig

from app import models
from app.models import App, UploadApk, Subject
from app.forms import AppForm, SubjectForm
from app.tables import AppTable, SubjectTable
from og.decorators import active_tab
from django_render_json import json as as_json
from django_render_json import render_json

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
def apps(request):
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


def render_jsonp(data, callback=None):
    if callback is None:
        return render_json(data, indent=4, ensure_ascii=False)

    import json
    content = callback + '(' + json.dumps(data, indent=4, ensure_ascii=False) + ')'
    return HttpResponse(content, content_type='text/plain')


def str_size(bits):
    if bits / pow(10, 6) > 0:
        return str(round(float(bits/pow(10, 6.0)), 2)) + 'MB'
    else:
        return str(round(float(bits/pow(10, 3.0)), 2)) + 'KB'


def permalink(host, path, scheme='http'):
    return scheme + '://' + host + path


def app_to_dict(app, host):
    result = model_to_dict(app)
    result.update({
        'file': permalink(host, app.apk.file.url),
        'size': str_size(app.size()),
        'icon': permalink(host, app.app_icon),
        'updateDate': app.update_date.strftime(u'%m-%d'),
        'longDescription': app.desc,
        'tags': [u'性能优化', u'流量'],
        'permissions': [
            u"显示系统级警报",
            u"查看 Wi-Fi 状态",
            u"控制振动器",
            u"拨打电话",
            u"读取基于网络的粗略位置",
            u"查看网络状态",
            u"修改全局系统设置"
         ],
         'system': u'Android 2.2.x以上',
         'total': u'1727 万'
    })

    screens = []
    for i in range(1, 7):
        img = result['screen' + str(i)]
        if img is not None and img != '':
            screens.append(permalink(host, img))
    result['screens'] = screens

    for i in range(1, 7):
        del result['screen' + str(i)]
    for key in ['app_icon', 'version_code', 'id', 'apk', 'longDesc']:
        del result[key]

    return result


@require_GET
def app(request, package):
    host = request.META['HTTP_HOST']
    callback = request.GET.get('callback', None)
    apps = App.objects.filter(package=package)
    data = apps[0] if apps.exists() else None
    if data is not None: 
        instance = app_to_dict(data, host)
    else:
        instance = data

    return render_jsonp({
        'app': instance
    }, callback);


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

    apps = App.objects.filter(name__contains=query)
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
def add_edit_subject(request):
    pk = request.POST["pk"]
    subject = Subject.objects.get(pk=int(pk))

    apps = request.POST.get("apps", None)
    apps = [] if not apps else [int(item) for item in apps.split(",")]
    models.edit_subject(subject, apps, request.user)

    return {'ret_code': 0}

 
def category(code):
    def handler(request):
        callback = request.GET.get('callback', None)
        subject = Subject.objects.get(code=code)
        return render_jsonp({
            'apps': map(lambda item: app_to_dict(item, request.META['HTTP_HOST']), subject.apps())
        }, callback)
        
    return handler


def ads(request):
    return render_jsonp({
        "main": {
            "cover": "http://ubmcmm.baidustatic.com/media/v1/0f000PLHkfGTh3aB7ncyYs.gif",
            "url": "http://jiaoyin.cm"
        },
        "side": {
            "cover": "http://ubmcmm.baidustatic.com/media/v1/0f0005UspaAo5OIP1PDpVf.gif",
            "url": "http://jiaoyin.cm"
        }
    }, request.GET.get('callback'))

