#!/bin/bash

python ./manage.py collectstatic
find /data/media/apks -type d -mtime +1 -exec rm -rf {} \;
find /data/media/apk_icons -type d -mtime +1 -exec rm -rf {} \;
find /data/media/upload -type f -mtime +1 -exec rm {} \;
find /data/media/ajax_uploads -type f -mtime +1 -exec rm {} \;

