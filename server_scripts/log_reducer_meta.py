#!/usr/bin/env python
dbhost = 'dev-node1.limijiaoyin.com'
dbport = 3306
dbuser = 'root'
dbpass = 'nameLR9969'
dbname = 'tianyin'

import _mysql
import sys
import HTMLParser
import json
import datetime

lastDay = datetime.date.today() - datetime.timedelta(days=0)

db = _mysql.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
db.query("DELETE FROM interface_logmeta WHERE date ='%s';" % (lastDay.isoformat(),))
r = db.store_result()
for line in sys.stdin:
    print line
