# -*- coding: utf-8 -*-
from django_select2 import *

class Select2WidgetCN(Select2Widget):
	def init_options(self):
		super(Select2WidgetCN, self).init_options()
		self.options['formatNoMatches'] = util.JSFunction('select2_no_matches')
		self.options['formatSearching'] = util.JSFunction('select2_searching')
