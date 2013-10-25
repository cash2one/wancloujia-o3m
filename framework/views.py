import logging

from django.contrib import auth
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger(__name__)

@require_GET
def welcome(request):
    if request.user.is_authenticated():
        return redirect("/index")
    else:
        return render(request, "login.html") 

@login_required
@require_GET
def index(request):
    logger.debug('index')
    return render(request, "index.html")

@login_required
@require_GET
def logout(request):
    auth.logout(request)
    return redirect("/welcome")

