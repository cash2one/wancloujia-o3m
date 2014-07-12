from django import forms
from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

import urllib2

from ajax_upload.models import UploadedFile


class AjaxUploadException(Exception):
    pass


class AjaxClearableFileInput(forms.TextInput):
    template_with_clear = ''  # We don't need this
    template_with_initial = '%(input)s'

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        if value:
            filename = value
        else:
            filename = ''
        attrs.update({
            'type': 'file',
            'class': attrs.get('class', '') + 'ajax-upload',
            'data-filename': filename,  # This is so the javascript can get the actual value
            'data-required': self.is_required or '',
            'data-upload-url': reverse('ajax-upload')
        })
        output = super(AjaxClearableFileInput, self).render(name, value, attrs)
        return mark_safe(output)
