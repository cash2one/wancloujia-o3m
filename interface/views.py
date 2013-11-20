# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, renderer_classes
from interface.models import LogEntity
from interface.serializer import LogSerializer
from django.contrib import auth
from mgr.models import Staff
from app.models import Subject
from app.models import App
from serializers import AppSerializer

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
    Subject.objects.all()
    pass

@api_view(['GET', 'POST'])
@parser_classes((JSONParser,))
#@renderer_classes((JSONRenderer,))
def subject_apps(request):
    if request.DATA and 'id' in request.DATA:
        return Response({'status': 'with id ' + str(request.DATA['id']) } )
    #return Response({'status': 'no id'})
    apps = App.objects.all()
    serializer = AppSerializer(apps)
    return Response(serializer.data)



@api_view(['GET','POST'])
@parser_classes((JSONParser,))
def echo(request):
    return Response(request.DATA)