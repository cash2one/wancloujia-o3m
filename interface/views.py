# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, renderer_classes
from interface.models import LogEntity
from interface.serializer import LogSerializer
from django.contrib import auth
from mgr.models import Staff
from app.models import Subject
from app.models import App, AppGroup
from serializers import AppSerializer, SubjectSerializer

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
def upload(request):
    if request.method == "POST":
        return HttpResponse(status=400)
    return HttpResponse(status=202)


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

@api_view(['GET'])
@parser_classes((JSONParser,))
def user_logout(request):
    return Response({"status":"ok"})

@api_view(['GET'])
@parser_classes((JSONParser,))
def all_subjects(request):
    subjects = Subject.objects.filter(online=True).order_by('-position')
    result = [
        {
            "id": item.id,
            "name": item.name,
            "cover": item.cover,
            "desc": item.desc,
            "size": get_subject_total_size(item),
        } for item in subjects]
    return Response(result)


def get_subject_total_size(subject):
    apps = get_apps_by_subject_id(subject.id)
    size = reduce(lambda acc, i: acc + i.size(), apps, 0)
    return size


def get_apps_by_subject_id(subject_id):
    subject = Subject.objects.get(id=subject_id)
    apps_in_subject = AppGroup.objects.filter(subject=subject)
    apps = filter(lambda i: i.online, [item.app for item in apps_in_subject])
    return apps

@api_view(['GET', 'POST'])
@parser_classes((JSONParser,))
#@renderer_classes((JSONRenderer,))
def subject_apps(request):
    if request.DATA and 'id' in request.DATA:
        apps = get_apps_by_subject_id(request.DATA['id'])
        serializer = AppSerializer(apps)
        return Response(serializer.data)
    apps = App.objects.all()
    serializer = AppSerializer(apps)
    for idx, item in enumerate(serializer.data):
        item['size'] = apps[idx].size()
    return Response(serializer.data)


@api_view(['GET','POST'])
@parser_classes((JSONParser,))
def echo(request):
    return Response(request.DATA)


def wandoujia_subjects(request):
    return render(request, "wandoujia/subjects.html")


def wandoujia_apps(request, id):
    return render(request, "wandoujia/apps.html")
