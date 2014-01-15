# coding: utf-8
import logging
import datetime
import time
import re
from functools import wraps
from hashlib import md5

from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import auth

from rest_framework import status
from rest_framework.renderers import JSONRenderer, UnicodeJSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, renderer_classes

from serializers import AppSerializer, SubjectSerializer
from suning import settings
from suning import utils
from interface.models import LogMeta
from interface.storage import hdfs_storage
from mgr.models import Staff
from app.models import Subject, App, AppGroup, SubjectMap
from app.tables import bitsize
from ad.models import AD

import zlib
from django.core.cache import cache

import urllib

logger = logging.getLogger('windows2x.post')
@parser_classes(JSONParser,)
@renderer_classes(JSONRenderer,)
def create_feedface(request):
    return HttpResponse(status=200)

def find_username(uid, cache):
    if cache.has_key(uid):
        return cache[uid]
    else:
        try:
            result = Staff.objects.get(pk=uid)
            cache[uid] = result.username
            return result.username
        except:
            return u'未知用户'

def find_subject(sid, cache):
    if cache.has_key(sid):
        return cache[sid]
    else:
        try:
            result = Subject.objects.get(pk=sid)
            cache[sid] = result.name
            return cache[sid]
        except:
            return u'未知专题'

@api_view(['GET', 'POST'])
@renderer_classes((UnicodeJSONRenderer,),)
def export(request):
    users = {}
    subjs = {}
    dt = datetime.date.today().isoformat()
    if request.method == "GET":
        dt = request.GET.get('upload_dt',datetime.date.today().isoformat())
    elif request.method == "POST":
        dt = request.POST.get('upload_dt',datetime.date.today().isoformat())
    dt = datetime.datetime.strptime(dt, '%Y-%m-%d')
    result =[{"model": i.model, "imei": i.did, "batch_no": 0, "install_dt":i.date, "info":find_subject(i.subject, subjs),
              "result":i.installed,"account":find_username(i.uid, users),"version":i.client_version}
             for i in LogMeta.objects.filter(date=dt)]
    return Response(result)

@api_view(['GET', 'POST'])
def get_hdfs_file(request, addr):
    if '..' in addr or '~' in addr:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    addr = settings.MEDIA_ROOT + addr
    offset = 0
    if 'Range' in request.META:
        reResult = re.match(r'^bytes=(?P<offset>\d+)', request.META['Range'])
        if 'offset' in reResult.groupdict() and reResult['offset']:
            offset = int(reResult.groupdict(['offset']))
        else:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    dfs = hdfs_storage()
    blks = dfs.enum_file(addr, offset)
    if 'Range' in request.META:
        result = HttpResponse(blks, status=206)
        result['Content-Range'] = 'bytes %ld-%ld/%ld' % (blks.offset, blks.size - 1 if blks.size - 1 >= 0 else 0,
                                                         blks.size)
        result['Content-Length'] = str(blks.remain)
        result['Content-Type'] = 'application/octet-stream'
        return result
    else:
        result = HttpResponse(blks)
        result['Content-Length'] = str(blks.remain)
        result['Content-Type'] = 'application/octet-stream'
        return result


@csrf_exempt
@api_view(['GET', 'POST'])
def upload(request):
    if request.method == "POST":
        log = zlib.decompress(str(request.raw_post_data), 16+zlib.MAX_WBITS, 16384)
        logger.info(log)
        return HttpResponse(status=status.HTTP_201_CREATED)
    return HttpResponse(status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['GET', 'POST'])
def feedback(request):
    return HttpResponse(status=status.HTTP_201_CREATED)

def set_cookie(response, key, value, days_expire = 14):
    max_age = days_expire * 24 * 60 * 60 
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires)


def login_test(func):
    @wraps(func)
    def wrap(request, *args, **kwargs):
        value = request.COOKIES.get("username")
        if not value:
            return redirect("/interface/welcome")

        return func(request, *args, **kwargs)
    return wrap


@require_GET
def welcome(request):
    if request.user.is_authenticated():
        request.session['wandoujia'] = True
        return redirect("/interface/subjects")
    else:
        c = cache.get("interface.welcome", None)
        if c:
            return c
        else:
            c = render(request, "login.html", {"wandoujia": "true"})
            cache.set("interface.welcome", c , 30)
            return c


@require_GET
@login_required(login_url='/interface/welcome')
def logout(request):
    auth.logout(request)
    return redirect("/interface/welcome")


@require_GET
def subjects(request):
    return render(request, "wandoujia/subjects.html")


def create_filter(model, bits):
    def _filter(subject):
        rules = SubjectMap.objects.filter(subject=subject)

        if len(rules) == 0:
            return True

        for rule in rules:
            if rule.match(model, bits):
                return True
        return False

    return _filter


@require_GET
def getSubjects(request):
    if not request.user.is_authenticated():
        return utils.render_json({"ret_code": 0, "subjects": []})

    model = request.GET.get("model") or None
    size = request.GET.get("size")
    bits = int(size) if size else None

    subjects = Subject.objects.all().order_by("position")
    if model != None and bits != None:
        rules_filter = create_filter(model, bits)
        subjects = filter(rules_filter, subjects)
    
    results = []
    for item in subjects:
        grps = AppGroup.objects.filter(subject=item).filter(app__online=True)
        if  grps.count() != 0:
            results.append({
                "id": item.pk,
                "name": item.name,
                "cover": item.cover,
                "desc": item.desc,
                "count": grps.count(),
                "size": bitsize(get_subject_total_size(item))
            })        

    return utils.render_json({"ret_code": 0, "subjects": results})


def get_subject_total_size(subject):
    grps = AppGroup.objects.filter(subject__pk=subject.pk).filter(app__online=True)
    return reduce(lambda acc, grp: acc + grp.app.size(), grps, 0)


@api_view(['GET', 'POST'])
@parser_classes((JSONParser,))
def echo(request):
    return Response(request.DATA)


def _file_md5(path):
    with open(path, 'rb') as f:
        m = md5()
        m.update(f.read())
        return m.hexdigest()


def _get_app(grp):
    app = grp.app
    return {
        "id": app.pk,
        "md5": _file_md5('/data/nfs_mirror' + app.apk.file.path),
        "package": app.package,
        "name":  app.name,
        "icon": app.app_icon,
        "desc": app.desc,
        "version": app.version,
        "size": bitsize(app.size()),
        "bits": app.size(),
        "apk": app.apk.file
    }


@require_GET
@login_required(login_url='/interface/welcome')
def apps(request, id):
    subjects = Subject.objects.filter(pk=id)
    if len(subjects) == 0:
        return redirect("/interface/subjects")

    subject = subjects[0]    
    appgrps = AppGroup.objects.filter(subject=subject).order_by("position")
    if appgrps.count() == 0:
        return redirect("/interface/subjects")

    apps = map(_get_app, appgrps)
    return render(request, "wandoujia/apps.html", {
        "subject": subject, 
        "apps": apps
    })


