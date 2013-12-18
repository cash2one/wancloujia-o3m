# config begin
debug = True  # open->windows2x.log, false->windows2x.log.<lastday>
server_id = "1"
# config over
file = "/data/suning/logs/windows2x.log"
file_tmp = "/data/suning/logs/windows2x.tmp.log"

import re
import json
import os
import datetime

if debug:
	file = "/data/suning/logs/windows2x.log"
else:
	lastDay = datetime.date.today() - datetime.timedelta(days=1)
	file = "/data/suning/logs/windows2x.log.%d-%d-%d" % (lastDay.year, lastDay.month, lastDay.day)

headerRE = re.compile(r"^\[windows2x\](?P<header>.*)")
contentRE = re.compile(r"(?P<type>[a-zA-Z0-9_\.]+)\s(?P<content>\S+)\t\d+")

#os.popen("dos2unix " + file)

fp = open(file)
fp2 = open(file_tmp, "w")

def remap_log_content(content):
	result = re.match(contentRE, content)
	if result:
		resultdict = result.groupdict()
	else:
		resultdict = None
	if resultdict and "type" in resultdict and "content" in resultdict:
		if resultdict['type'] != "install":
			return
		j =json.loads(resultdict['content'])
		j["log_type"] = resultdict['type']
		encodedjson = json.dumps(j)
		fp2.write(encodedjson + "\n")

for i in fp.readlines():
	result = re.match(headerRE, i);
	if result:
		resultdict = result.groupdict()
	else:
		resultdict = None
	if resultdict and "header" in resultdict:
		pass #new log header
	else:
		remap_log_content(i)
fp.close()
fp2.close()
if debug == True:
    lastDay = datetime.date.today()
else:
    lastDay = datetime.date.today() - datetime.timedelta(days=1)
file = "windows2x.log.%d-%d-%d" % (lastDay.year, lastDay.month, lastDay.day)
app_cmd = '/opt/hadoop/hadoop-2.2.0/bin/hadoop fs -put -f ' + file_tmp + ' /logs/' + file + '.' + server_id + " && rm " + file_tmp
os.popen(app_cmd)
if debug:
	file = "/data/suning/logs/windows2x.log"
else:
	lastDay = datetime.date.today() - datetime.timedelta(days=1)
	file = "/data/suning/logs/windows2x.log.%d-%d-%d" % (lastDay.year, lastDay.month, lastDay.day)
if not debug:
    pass
	#os.popen('rm ' + file)

