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
from django.conf import settings as django_settings

from rest_framework import status
from rest_framework.renderers import JSONRenderer, UnicodeJSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, renderer_classes

from serializers import AppSerializer, SubjectSerializer
#TODO 使用正确的获取settings的方式
from suning import settings
from suning import utils
from interface.models import LogMeta
# from interface.storage import hdfs_storage
from mgr.models import Staff
from app.models import Subject, App, AppGroup, SubjectMap
from app.tables import bitsize
from ad.models import AD
import re
import zlib
from django.core.cache import cache
import json
import urllib
from interface.models import LogEntity

headerRE2 = re.compile(r"clientVersion=(?P<client>[^,]+),")
contentRE2 = re.compile(r"^(?P<content>[^\t]+)\s(?P<content2>[^\s]+)\s\d+")
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

def get_pici(subj_name):
    pici = ''
    try:
        m = re.match(r'^[^\#]*\#[^\#]*\#(?P<pici>.*)', subj_name).groupdict()
        pici = m['pici']
    except:
        pass
    return pici

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
    result =[{"model": i.model, "imei": i.did, "batch_no": get_pici(find_subject(i.subject, subjs)), "install_dt":i.date, "info":find_subject(i.subject, subjs),
              "result":i.installed,"account":find_username(i.uid, users),"version":i.client_version}
             for i in LogMeta.objects.filter(date=dt)]
    return Response(result)

def remap_log_content(content, version="1.0.0.0"):
    result2 = re.match(contentRE2, content)
    if content.find("tianyin.install") > -1 and result2:
        resultdict = result2.groupdict()
    else:
        resultdict = None
    if resultdict and "content" in resultdict and "content2" in resultdict:
        j =json.loads(resultdict['content'])
        k = json.loads(resultdict['content2'])
        j["log_type"] = 'success' if j['event'] == 'tianyin.install.success' else 'install'
        j['deviceId'] = k['deviceId']
        j['client'] = version
        encodedjson = json.dumps(j)
        entity = LogEntity()
        entity.create = datetime.date.today()
        entity.content = encodedjson
        entity.save()

def savelog(arr):
    version = "1.0.0.0"
    for i in arr:
        try:
            i = i.strip()
            result = re.match(headerRE2, i)
            if result: #判断是不是日志报头
                resultdict = result.groupdict()
            else:
                resultdict = None
            if resultdict:
                if resultdict and "client" in resultdict:
                    version = resultdict['client']
                else:
                    version = "未知"
            else:   #不是日志报头的，交给这个函数处理i
                remap_log_content(i, version)
        except:
            pass

@csrf_exempt
@api_view(['GET', 'POST'])
def upload(request):
    if request.method == "POST":
        log = zlib.decompress(str(request.raw_post_data), 16+zlib.MAX_WBITS, 16384)
        savelog(log.split('\n'))
        return HttpResponse(status=status.HTTP_200_OK)
    return HttpResponse(status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['GET', 'POST'])
def signal(request):
    if request.method == "POST":
        log = "logs begin"
        logger.info(log)
        return HttpResponse(status=status.HTTP_200_OK)
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
    logger = logging.getLogger('default')
    logger.debug("!!!media root: " + settings.MEDIA_ROOT)
    return render(request, "wandoujia/subjects.html", {'development': django_settings.DEBUG})


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
    #return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    logger = logging.getLogger('default')
    logger.debug("get Subjects")

    if not request.user.is_authenticated():
        logger.debug("user no authenticated")
        return utils.render_json({"ret_code": 0, "subjects": []})

    model = request.GET.get("model") or None
    size = request.GET.get("size")
    bits = int(size) if size else None

    logger.debug("model: " + str(model))
    logger.debug("size: " + str(size))
    logger.debug("bits: " + str(bits))

    subjects = None
    if model != None:
        maps = SubjectMap.objects.filter(model__ua=model)
        logger.debug("subject maps count: " + str(len(maps)))
        if len(maps) != 0:
            subjects = [maps[0].subject]

    if subjects is None and bits != None:
        maps = SubjectMap.objects.filter(mem_size=SubjectMap.getMemSize(bits))
        logger.debug("subject maps count: " + str(len(maps)))
        if len(maps) != 0:
            subjects = [maps[0].subject]

    if subjects is None:
        subjects = Subject.objects.all().order_by("position")
    
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
    #return utils.render_json({"ret_code": 1})
    #return utils.render_json({"ret_code": 0, "subjects": []})


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
        "md5": app.apk.md5,
        "package": app.package,
        "name":  app.name,
        "icon": app.app_icon,
        "desc": app.desc,
        "version": app.version,
        "size": bitsize(app.apk.size),
        "bits": app.apk.size,
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
        "apps": apps,
        'development': django_settings.DEBUG
    })


