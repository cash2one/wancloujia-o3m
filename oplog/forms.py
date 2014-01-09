from django import forms
from oplog.models import OPLOG_TYPE_CHOICE
from mgr.models import Staff
from datetime import datetime

def get_users():
	users = [(i.pk, i.username) for i in Staff.objects.all()]
	users = sorted(users, key=lambda x:x[1])
	return users

class OpLogForm(forms.Form):
	username = forms.ChoiceField(choices=[(-1, "----")] + get_users(), initial=-1)
	from_date = forms.DateTimeField(initial=datetime.today())
	to_date = forms.DateTimeField(initial=datetime.today())
	type = forms.ChoiceField(choices=[(-1, '----')] + list(OPLOG_TYPE_CHOICE), initial=-1 )

