# coding: utf-8
from django.utils.safestring import mark_safe
import django_tables2 as tables

class AvailableColumn(tables.Column):
    def __init__(self, verbose_name=None, accessor=None, default=None, 
                        visible=True, orderable=None, attrs=None, order_by=None, 
                        sortable=None, empty_values=None, localize=None, available_text=u'显示', 
                        unavailable_text=u'隐藏'):
        super(AvailableColumn, self).__init__(verbose_name, accessor, default, visible, 
                                                orderable, attrs, order_by, sortable, 
                                                empty_values, localize)

        self.available_text =  available_text
        self.unavailable_text = unavailable_text

    def render(self, record):
        if not record.available():
            return self.unavailable_text

        if record.in_period():
            return self.available_text

        return mark_safe(u'''<p>显示</p>
                            <p class='warn'>！不在有效期内</p>''')
