#coding: utf-8
#!/usr/bin/env python
test = False
if test:
    dbhost = 'localhost'
    dbport = 3306
    dbuser = 'root'
    dbpass = 'nameLR9969'
    dbname = 'looyu'
else:
    dbhost = '172.31.21.201'
    dbport = 3306
    dbuser = 'wdj'
    dbpass = 'wdj'
    dbname = 'looyu'
    jobpath = '/opt/funtalk/server_scripts/'
debug = False
import _mysql
import sys
import HTMLParser
import json
import datetime

if len(sys.argv) < 2:
    lastDay = datetime.date.today() - datetime.timedelta(days=0 if debug else 1)
    datestr = lastDay.strftime("%Y-%m-%d")
else:
    datestr = sys.argv[1]
print "DELETE FROM interface_logmeta WHERE date ='%s';" % (datestr,)
for line in sys.stdin:
    print line
