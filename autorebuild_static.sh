#!/bin/bash
python ./manage.py collectstatic
find /home/wangnan/media/apks -type d -mtime +1 -exec rm -rf {} \;
find /home/wangnan/media/apk_icons -type d -mtime +1 -exec rm -rf {} \;
find /home/wangnan/media/upload -type f -mtime +1 -exec rm {} \;
find /home/wangnan/media/ajax_uploads -type f -mtime +1 -exec rm {} \;
