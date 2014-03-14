# -*- coding: utf-8 -*-
from django import forms
from oplog.models import OPLOG_TYPE_CHOICE
from mgr.models import Staff, cast_staff
from datetime import datetime
from django_select2 import *
from framework.widgets import Select2WidgetCN
from framework.templatetags.perm_filters import is_employee
from django.contrib.auth.models import User

class OpLogForm(forms.Form):
	username = Select2ChoiceField(choices=[], label=u'用户', widget=Select2WidgetCN())
	type_list = [(-1, '--------')]
	type_list.extend(OPLOG_TYPE_CHOICE)
	type = Select2ChoiceField(choices=type_list, required=True, label=u'操作', widget=Select2WidgetCN())
	from_date = forms.DateTimeField(initial=datetime.today())
	to_date = forms.DateTimeField(initial=datetime.today())


def get_form(request):
	if request.user.is_superuser or request.user.is_staff or request.user.has_perm('interface.view_all_data'):
		f = OpLogForm(request.POST)
		#username_list = [(-1, '--------')]
		#username_list.extend(Staff.objects.order_by('username').values_list('id', 'username'))
		#f.fields['username'] = Select2ChoiceField(choices=username_list, required=True, label=u'用户', widget=Select2WidgetCN())
		return f
	else:
		f = OpLogForm(request.POST)
		username_list = Staff.objects.filter(id=request.user.id).values_list('id', 'username')
		f.fields['username'] = Select2ChoiceField(choices=username_list, required=True, label=u'用户', widget=Select2WidgetCN())
		return f