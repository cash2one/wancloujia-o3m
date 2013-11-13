# encoding: utf-8
import re

from django import forms
from parsley.decorators import parsleyfy

from models import *

@parsleyfy
class AppForm(forms.ModelForm):

    class Meta:
        model = App

