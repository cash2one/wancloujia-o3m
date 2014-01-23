#!/usr/bin/env python
dbhost = '10.19.221.11'
dbport = 3306
dbuser = 'suningwdj'
dbpass = 'suningwdj'
dbname = 'suningwdj'

import _mysql
import sys
import HTMLParser
import json
import datetime

lastDay = datetime.date.today() - datetime.timedelta(days=0)
#db = _mysql.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
print "DELETE FROM interface_logmeta WHERE date ='%s';" % (lastDay.isoformat(),)
#r = db.store_result()
for line in sys.stdin:
    print line
