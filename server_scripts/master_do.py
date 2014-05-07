#coding: utf-8
# config begin
#数据库的配置
dbhost = 'localhost'
dbport = 3306
dbuser = 'root'
dbpass = 'nameLR9969'
dbname = 'tianyin'

#设置脚本的目录，末尾带斜杠
jobpath = '/data/tianyin.proj/tianyin/server_scripts/'

#是否删除hdfs上各个机器保留的日志拼接文件,建议False
remove_logs = False
#目标日志位置
targetdir = '/data/logs'
#是否处理昨天(而不是今天)的日志
last_day = False
import datetime
if last_day:
    lastDay = datetime.date.today() - datetime.timedelta(days=1)
else:
    lastDay = datetime.date.today()
#是否清理垃圾文件
auto_remove_files = False
#用于临时进行日志合并的目录
tmpdir = "/data/tianyin.proj/tianyin/logs"

#这里记录了hadoop需要执行的脚本以及结果存放的位置
jobs = [
		("log_mapper_meta.py", "log_reducer_meta.py", ),
		]
#config over
#########################################

print "import scripts"
import json
import datetime
import os
import HTMLParser
import _mysql
print "end load modules"

db = _mysql.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
db.query("SET NAMES utf8")
db.query("SET CHARACTER_SET_CLIENT=utf8")
db.query("SET CHARACTER_SET_RESULTS=utf8")

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
tmp = {}
for i in files:
    tmp[i] = True
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
for i in files:
	try:
            if auto_remove_files:
                os.remove(i)
	except:
		pass
#raise NameError()
print "config hadoop"
filename = targetdir + "/windows2x.log.%s" % (lastDay.isoformat(),)
#dump 数据库到本地文件
fp = open(filename, "w")
db.query("SELECT content FROM interface_logentity;" )
r = db.store_result()
n = r.num_rows()
for i in range(0, n):
    content = r.fetch_row()[0][0]
    fp.write(content + "\n")
fp.close()
print "begin clean db"
sqlexe = '/usr/bin/mysql -u%s -p%s -h%s --default-character-set=utf8 %s' % (dbuser, dbpass, dbhost, dbname)
os.popen('echo "DELETE FROM interface_logmeta WHERE date=\'%s\';" | %s' % (lastDay.isoformat(), sqlexe))
os.popen('echo "DELETE FROM interface_devicelogentity WHERE date=\'%s\';" | %s' % (lastDay.isoformat(), sqlexe))
os.popen('echo "DELETE FROM interface_userdevicelogentity WHERE date=\'%s\';" | %s' % (lastDay.isoformat(), sqlexe))
os.popen('echo "DELETE FROM interface_installedapplogentity WHERE date=\'%s\';" | %s' % (lastDay.isoformat(), sqlexe))

print "begin hadoop"
for map, red in jobs:
    cmd = "cat %s | /usr/local/bin/python2.7 %s%s | /usr/local/bin/python2.7 %s%s | %s" % \
          (filename, jobpath, map, jobpath, red, sqlexe  )
    os.popen(cmd)
if remove_logs:
    os.remove(filename)
print "hadoop over"
