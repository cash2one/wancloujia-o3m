from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ajax_upload.forms import UploadedFileForm
#from interface.storage import hdfs_storage
import os

@csrf_exempt
@require_POST
def upload(request):
    form = UploadedFileForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        uploaded_file = form.save()
        #dfs = hdfs_storage()
        #dfs.create(uploaded_file.file.path, uploaded_file.file.path)
        data = {
            'path': uploaded_file.file.url,
        }
        return HttpResponse(simplejson.dumps(data))
    else:
        return HttpResponseBadRequest(simplejson.dumps({'errors': form.errors}))
