#!/bin/bash

APPS="mgr statistics"

./manage.py test $APPS --settings=suning.settings_test
