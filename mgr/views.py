import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from mgr.models import cast_staff
from mgr.forms import ModifyPasswordForm

logger = logging.getLogger(__name__)

@require_GET
@login_required
def account(request):
    return render(request, "account.html", {
        "account": cast_staff(request.user), 
        "form": ModifyPasswordForm(),
        "active_tab": "account"
    })

@login_required
def user(request):
    return render(request, "user.html", {
        "account": cast_staff(request.user), 
        "form": ModifyPasswordForm()
    })

