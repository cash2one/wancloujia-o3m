#!/usr/bin/env python
dbhost = 'localhost'
dbport = 3306
dbuser = 'root'
dbpass = 'funtalkwdj'
dbname = 'funtalk'
debug = False
import _mysql
import sys
import HTMLParser
import json
import datetime

lastDay = datetime.date.today() - datetime.timedelta(days=0 if debug else 1)
#db = _mysql.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
print "DELETE FROM interface_logmeta WHERE date ='%s';" % (lastDay.isoformat(),)
#r = db.store_result()
for line in sys.stdin:
    print line
