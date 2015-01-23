import logging

from .models import Preference

logger = logging.getLogger(__name__)

def preference(request):
	return {
		'preference': Preference.getPreference()
	}

