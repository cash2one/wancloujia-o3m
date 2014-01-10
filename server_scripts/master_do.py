dbhost = 'dev-node1.limijiaoyin.com'
#dbport = 3306
dbuser = 'root'
dbpass = 'nameLR9969'
dbname = 'suning'
hadooppath = '/opt/hadoop/hadoop-2.2.0'
jobpath = '/home/songwei/logCount/'

hdfshost = 'dev-node1.limijiaoyin.com'
hdfsuser = 'songwei'
hdfsport = 50070

remove_logs = False
last_day = False
print "import scripts"
#config over
#os.popen("source /etc/profile")
import _mysql
import json
import datetime
import os
import HTMLParser
from pyhdfs import hdfs
print "end load modules"
hdfs.setConfig(hostname=hdfshost, port=str(hdfsport), username=hdfsuser)
db = _mysql.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
#scan hadoop fld
def scanHdfsFiles(pwd='/data', acc=[]):
    result = hdfs.listDirectory(pwd)
    dirs = []
    files = []
    for i in result:
        if i.fileType == 'DIRECTORY':
            dirs.append(i.path)
        else:
            files.append(i.path)
    acc += files
    for i in dirs:
        scanHdfsFiles(i, acc)


#apks/
def scan_ref_apk_files():
    header = '/data/media/'
    acc = set()
    db.query("SELECT app_uploadapk.file FROM app_app, app_uploadapk WHERE app_app.apk_id = app_uploadapk.id;")
    r = db.store_result()
    n = r.num_rows()
    for i in range(0, n):
        id = r.fetch_row()[0][0]
        acc.add(header + id)
    return acc

#/media/...
def scan_ref_apk_icon_files():
    header = '/data'
    acc = set()
    db.query("SELECT app_icon FROM app_app;")
    r = db.store_result()
    n = r.num_rows()
    for i in range(0, n):
        id = r.fetch_row()[0][0]
        acc.add(header + id)
    return acc


#ajax_uploads/
def scan_ref_ad_icon_files():
    header = '/data/media/'
    acc = set()
    db.query("SELECT cover FROM ad_ad;")
    r = db.store_result()
    n = r.num_rows()
    for i in range(0, n):
        id = r.fetch_row()[0][0]
        acc.add(header + id)
    return acc

#/media/ajax_uploads/
def scan_ref_subject_icon_files():
    header = '/data'
    acc = set()
    db.query("SELECT cover FROM app_subject;")
    r = db.store_result()
    n = r.num_rows()
    for i in range(0, n):
        id = r.fetch_row()[0][0]
        acc.add(header + id)
    return acc
print "begin cleanup"
files = []
scanHdfsFiles(acc=files)
tmp = {}
for i in files:
    tmp[i.encode('utf8')] = True
files = tmp
apks = scan_ref_apk_files()
apkicons = scan_ref_apk_icon_files()
adicons = scan_ref_ad_icon_files()
subjecticons = scan_ref_subject_icon_files()
refed = list(apks | apkicons | adicons | subjecticons)
tmp = []
html_parser = HTMLParser.HTMLParser()
import urllib
for i in refed:
    tmp.append(urllib.unquote(i))
refed = tmp
for i in refed:
    if i in files:
        del files[str(i)]
files = sorted(files)
for i in files:
	try:
		print i
		#hdfs.remove(i, True)
	except:
		pass
if last_day:
    lastDay = datetime.date.today() - datetime.timedelta(days=1)
else:
    lastDay = datetime.date.today()

print "config hadoop"
filename = "/data/suning/tmp/windows2x.log.%s" % (lastDay.isoformat(),)
dstfilename = "/logs/windows2x.log.%s" % (lastDay.isoformat(),)
os.popen("rm -f %s" % filename)
os.popen("/opt/hadoop/hadoop-2.2.0/bin/hadoop fs -getmerge  %s.* %s" % (dstfilename, filename))
os.popen("/opt/hadoop/hadoop-2.2.0/bin/hadoop fs -put -f %s %s" % (filename, dstfilename))
os.popen("rm -f %s" % filename)
os.popen("/opt/hadoop/hadoop-2.2.0/bin/hadoop fs -rm -f %s.*" % dstfilename)

print "begin clean db"
sqlexe = 'mysql -u%s -p%s -h%s %s' % (dbuser, dbpass, dbhost, dbname)
os.popen('echo "DELETE FROM interface_logmeta WHERE date=\'%s\'" | %s' % (lastDay.isoformat(), sqlexe))
os.popen('echo "DELETE FROM interface_devicelogentity WHERE date=\'%s\' | %s"' % (lastDay.isoformat(), sqlexe))
os.popen('echo "DELETE FROM interface_userdevicelogentity WHERE date=\'%s\'" | %s' % (lastDay.isoformat(), sqlexe))
os.popen('echo "DELETE FROM interface_installedapplogentity WHERE date=\'%s\'" | %s' % (lastDay.isoformat(), sqlexe))
print "begin hadoop"
jobs = [
		("log_mapper_meta.py", "log_reducer_meta.py", "/logs/meta%s" % (lastDay.isoformat(), )),
		("log_mapper_appstat.py", "log_reducer_appstat.py", "/logs/appstat%s" % (lastDay.isoformat(),)),
		("log_mapper_devicelog.py", "log_reducer_devicelog.py", "/logs/device%s" % (lastDay.isoformat(), )),
		("log_mapper_userdev.py", "log_reducer_userdev.py", "/logs/userdev%s" % (lastDay.isoformat(), )),
		]


input = "/logs/windows2x.log.%s" % (lastDay.isoformat(), )
hadoop = hadooppath + "/bin/hadoop"
hadoop_jar = hadooppath + "/share/hadoop/tools/lib/hadoop-streaming-2.2.0.jar"
for map, red, output in jobs:
	cmd = "%s jar %s -mapper %s -reducer %s -input %s -output %s"  % \
		( hadoop, hadoop_jar, jobpath + map, jobpath + red, input, output)
	os.popen(cmd)
	cmd = "%s fs -cat %s | mysql -u%s -p%s -h%s %s" % ( hadoop, output+ "/part*" , dbuser, dbpass, dbhost, dbname)
	os.popen(cmd)
for map, red, output in jobs:
	cmd = "%s fs -rm -r -f %s" % (hadoop, output)
	os.popen(cmd)
if remove_logs:
	cmd = "%s fs -rm -f %s" % (hadoop, input)
	os.popen(cmd)
print "hadoop over"
