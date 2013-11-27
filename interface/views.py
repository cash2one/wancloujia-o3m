# coding: utf-8
import logging
import datetime
from functools import wraps

from django.http import HttpResponse
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import auth

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, renderer_classes

from serializers import AppSerializer, SubjectSerializer
from suning import settings
from interface.models import LogEntity
from interface.serializer import LogSerializer
from framework.forms import LoginForm
from mgr.models import Staff
from app.models import Subject, App, AppGroup
from app.tables import bitsize
from ad.models import AD

import zlib


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRednderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def snippet_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        log = LogEntity.objects.get(pk=pk)
    except LogEntity.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = LogSerializer(log)
        return JSONResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = LogSerializer(log, data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data)
        else:
            return JSONResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        log.delete()
        return HttpResponse(status=204)

@csrf_exempt
@api_view(['GET', 'POST'])
def upload(request):
    if request.method == "POST":
        #log = request.raw_post_data
        log = zlib.decompress(str(request.raw_post_data), 16+zlib.MAX_WBITS, 16384)
        logger.info(log)
        return HttpResponse(status=status.HTTP_201_CREATED)
    return HttpResponse(status=status.HTTP_404_NOT_FOUND)


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
    if request.COOKIES.get("username"):
        return redirect("/interface/subjects")
    else:
        return render(request, "login.html", {"wandoujia": "true"}) 

@require_POST
def login(request):
    username = request.POST["username"]
    password = request.POST["password"]
    form = LoginForm({'username': username, 'password': password})
    if not form.is_valid():
        logger.debug("form is invalid")    
        return HttpResponse(simplejson.dumps({
            'ret_code': 1000, 
            'ret_msg': u'用户名或密码不正确！'
        }), mimetype='application/json')

    data = form.cleaned_data
    logger.debug("username: %s; password: %s" % (data['username'], data['password']))
    user = auth.authenticate(username=data['username'], password=data['password'])
    if user is None:
        logger.debug("user is not authenticated")
        return HttpResponse(simplejson.dumps({
            'ret_code': 1000, 
            'ret_msg': u'用户名或密码不正确！'
        }), mimetype='application/json')

    if not user.is_active:
        logger.debug("user is not active")
        return HttpResponse(simplejson.dumps({
            'ret_code': 1000, 
            'ret_msg': u'账号被锁定，登录失败！'
        }), mimetype='application/json')
    logger.debug("user is authenticated")

    response = HttpResponse(simplejson.dumps({'ret_code': 0}), mimetype='application/json')
    set_cookie(response, "username", username)
    return response


@require_GET
@login_test
def logout(request):
    response = redirect("/interface/welcome")
    response.delete_cookie("username")
    return response


@require_GET
@login_test
def subjects(request):
    subjects = Subject.objects.filter(online=True).order_by('position')
    now = datetime.datetime.now()
    ads = AD.objects.filter(visible=True).filter(from_date__lt=now).filter(to_date__gt=now).order_by('position')
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
                "size": bitsize(get_subject_total_size(item)),       
            })        
    
    #return render(request, "wandoujia/subjects.html", {"subjects": [], "ads": []})
    return render(request, "wandoujia/subjects.html", {"subjects": results, "ads": ads})


def get_subject_total_size(subject):
    grps = AppGroup.objects.filter(subject__pk=subject.pk).filter(app__online=True)
    return reduce(lambda acc, grp: acc + grp.app.size(), grps, 0)



@api_view(['GET', 'POST'])
@parser_classes((JSONParser,))
def echo(request):
    return Response(request.DATA)


def _get_app(grp):
    app = grp.app
    return {
        "id": app.pk,
        "name":  app.name,
        "icon": app.app_icon,
        "desc": app.desc,
        "version": app.version,
        "size": bitsize(app.size()),
        "bits": app.size(),
        "apk": app.apk.file
    }


@require_GET
@login_test
def apps(request, id):
    subjects = Subject.objects.filter(pk=id)
    if len(subjects) == 0:
        return redirect("/interface/subjects")

    subject = subjects[0]    
    appgrps = AppGroup.objects.filter(subject=subject).order_by("position")
    if appgrps.count() == 0:
        return redirect("/interface/subjects")

    apps = map(_get_app, appgrps)
    return render(request, "wandoujia/apps.html", {"subject": subject, "apps": apps})



logger = logging.getLogger('windows2x.post')
logger.setLevel(logging.INFO)
filename = 'logs/windows2x'
hdlr = logging.handlers.TimedRotatingFileHandler(filename, 'M', 1, 7)
hdlr.suffix = '%Y-%m-%d.log'
formatter = logging.Formatter('[windows2x]%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
