#coding: utf-8
# config begin
#数据库的配置
dbhost = '10.19.221.11'
dbuser = 'suningwdj'
dbpass = 'suningwdj'
dbname = 'suningwdj'

# #设置hadoop的位置
# hadooppath = '/opt/hadoop/hadoop-2.2.0'
#设置脚本的目录，末尾带斜杠
jobpath = '/opt/suning/server_scripts/'

# #设置web hdfs的位置
# hdfshost = 'dev-node1.xxx.com'
# hdfsuser = 'songwei'
# hdfsport = 50070

#是否删除hdfs上各个机器保留的日志拼接文件
remove_logs = True
#目标日志位置
targetdir = '/data/logs'
#是否处理昨天(而不是今天)的日志
last_day = False
import datetime
if last_day:
    lastDay = datetime.date.today() - datetime.timedelta(days=1)
else:
    lastDay = datetime.date.today()

#用于临时进行日志合并的目录
tmpdir = "/opt/suning/tmp"

#这里记录了hadoop需要执行的脚本以及结果存放的位置
jobs = [
		("log_mapper_meta.py", "log_reducer_meta.py", "/logs/meta.%s" % (lastDay.isoformat(), )),
		("log_mapper_appstat.py", "log_reducer_appstat.py", "/logs/appstat.%s" % (lastDay.isoformat(),)),
		("log_mapper_devicelog.py", "log_reducer_devicelog.py", "/logs/device.%s" % (lastDay.isoformat(), )),
		("log_mapper_userdev.py", "log_reducer_userdev.py", "/logs/userdev.%s" % (lastDay.isoformat(), )),
		]
#config over
#########################################

print "import scripts"
import json
import datetime
import os
import HTMLParser
import _mysql
#from pyhdfs import hdfs
print "end load modules"
#hdfs.setConfig(hostname=hdfshost, port=str(hdfsport), username=hdfsuser)
db = _mysql.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
#scan hadoop fld
# def scanHdfsFiles(pwd='/data', acc=[]):
#     result = hdfs.listDirectory(pwd)
#     dirs = []
#     files = []
#     for i in result:
#         if i.fileType == 'DIRECTORY':
#             dirs.append(i.path)
#         else:
#             files.append(i.path)
#     acc += files
#     for i in dirs:
#         scanHdfsFiles(i, acc)

def scan_files(pwd='/data/media', acc=[]):
    for root,dirs,files in os.walk(pwd):
        for filespath in files:
            acc.append(os.path.join(root, filespath))
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
scan_files(acc=files)
#scanHdfsFiles(acc=files)
tmp = {}
for i in files:
    tmp[i] = True
    #tmp[i.decode('utf8')] = True
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
        del files[i]
#for i in sorted(list(refed)):
#    print i
#print "--------------"
#print "--------------"
#files = sorted(files)
for i in files:
	try:
		#print i
            os.popen('rm %s', i)
		#hdfs.remove(i, True)
	except:
		pass

print "config hadoop"
filename = targetdir + "/windows2x.log.%s" % (lastDay.isoformat(),)
# dstfilename = "/logs/windows2x.log.%s" % (lastDay.isoformat(),)
# hadoop = hadooppath + "/bin/hadoop"
#
# os.popen("rm -f %s" % filename)
# os.popen(hadoop + " fs -getmerge  %s.* %s" % (dstfilename, filename))
# os.popen(hadoop + " fs -put -f %s %s" % (filename, dstfilename))
# os.popen("rm -f %s" % filename)
# os.popen(hadoop + " fs -rm -f %s.*" % dstfilename)
#合并文件段为一个文件
os.popen("cat %s.* > %s" % (filename, filename,))
print "begin clean db"
sqlexe = 'mysql -u%s -p%s -h%s %s' % (dbuser, dbpass, dbhost, dbname)
os.popen('echo "DELETE FROM interface_logmeta WHERE date=\'%s\';" | %s' % (lastDay.isoformat(), sqlexe))
os.popen('echo "DELETE FROM interface_devicelogentity WHERE date=\'%s\';" | %s' % (lastDay.isoformat(), sqlexe))
os.popen('echo "DELETE FROM interface_userdevicelogentity WHERE date=\'%s\';" | %s' % (lastDay.isoformat(), sqlexe))
os.popen('echo "DELETE FROM interface_installedapplogentity WHERE date=\'%s\';" | %s' % (lastDay.isoformat(), sqlexe))

print "begin hadoop"
#input = dstfilename
# hadoop_jar = hadooppath + "/share/hadoop/tools/lib/hadoop-streaming-2.2.0.jar"
for map, red, output in jobs:
    cmd = "cat %s | python %s%s | python %s%s | %s" % \
          (filename, jobpath, map, jobpath, red, sqlexe  )
	# cmd = "%s jar %s -mapper %s -reducer %s -input %s -output %s"  % \
	# 	( hadoop, hadoop_jar, jobpath + map, jobpath + red, input, output)
    os.popen(cmd)
	# cmd = "%s fs -cat %s | %s" % ( hadoop, output+ "/part*" , sqlexe)
	# os.popen(cmd)
# for map, red, output in jobs:
# 	cmd = "%s fs -rm -r -f %s" % (hadoop, output)
# 	os.popen(cmd)
if remove_logs:
	cmd = "rm -f %s.*" % (filename,)
	os.popen(cmd)
print "hadoop over"
