# coding: utf-8
import logging
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import auth

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, renderer_classes

from serializers import AppSerializer, SubjectSerializer
from interface.models import LogEntity
from interface.serializer import LogSerializer
from mgr.models import Staff
from app.models import Subject, App, AppGroup
from app.tables import bitsize
from ad.models import AD


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
        logger.info(request.raw_post_data)
        return HttpResponse(request.raw_post_data)
    return HttpResponse(request.DATA)


@api_view(['GET'])
@parser_classes((JSONParser,))
def user_login(request, username, password):
    if request.method == "GET":
        user = Staff.objects.filter(username=username)
        if user and auth.authenticate(username=username,password=password):
            #auth.login(request,user)
            return Response({"status": "ok"})
        elif len(user) == 0:
            return Response({"status": "user not exist"})
        else:
            return Response({"status": "wrong password"})
    else:
        return Response({"status": "wrong method"})


@require_GET
@login_required
def logout(request):
    auth.logout(request)
    return redirect("/interface/welcome")


@require_GET
@login_required(login_url="/interface/welcome")
def subjects(request):
    subjects = Subject.objects.filter(online=True).order_by('position')
    now = datetime.now()
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
        "name":  app.name,
        "icon": app.app_icon,
        "desc": app.desc,
        "version": app.version,
        "size": bitsize(app.size()),
        "bits": app.size(),
        "apk": app.apk.file
    }

@require_GET
@login_required(login_url="/interface/welcome")
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

@require_GET
def welcome(request):
    if request.user.is_authenticated():
        return redirect("/interface/subjects")
    else:
        return render(request, "login.html") 


logger = logging.getLogger('post_logger')
logger.setLevel(logging.INFO)
filename = 'logs/post'
hdlr = logging.handlers.TimedRotatingFileHandler(filename, 'M', 1, 7)
hdlr.suffix = '%Y%m%d.log'
logger.addHandler(hdlr)
