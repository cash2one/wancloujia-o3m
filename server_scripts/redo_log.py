#coding: utf-8
# config begin
import sys
test = False
#数据库的配置
if test:
    dbhost = 'localhost'
    dbport = 3306
    dbuser = 'root'
    dbpass = 'nameLR9969'
    dbname = 'looyu'
    jobpath = '/data/looyu/server_scripts/'
else:
    dbhost = '172.31.21.201'
    dbport = 3306
    dbuser = 'wdj'
    dbpass = 'wdj'
    dbname = 'looyu'
    jobpath = '/opt/funtalk/server_scripts/'

#设置脚本的目录，末尾带斜杠

#是否删除hdfs上各个机器保留的日志拼接文件
remove_logs = False
#目标日志位置
targetdir = '/data/logs'
import datetime

#用于临时进行日志合并的目录
tmpdir = "/opt/suning/tmp"

#这里记录了hadoop需要执行的脚本以及结果存放的位置
#config over
#########################################

print "import scripts"
import json
import datetime
import os
import HTMLParser
import _mysql
print "end load modules"

startday = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
runday = startday
endday = datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d").date()
print startday, endday

db = _mysql.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
db.query("SET NAMES utf8")
db.query("SET CHARACTER_SET_CLIENT=utf8")
db.query("SET CHARACTER_SET_RESULTS=utf8")

while runday <= endday:
    print runday
    datestr = runday.strftime("%Y-%m-%d")
    jobs = [
        ("log_mapper_meta.py %s" % datestr, "log_reducer_meta.py %s" % datestr, "/logs/meta.%s" % datestr),
        ("log_mapper_appstat.py %s" % datestr, "log_reducer_appstat.py %s" % datestr, "/logs/appstat.%s" % datestr),
        ("log_mapper_devicelog.py %s" % datestr, "log_reducer_devicelog.py %s" % datestr, "/logs/device.%s" % datestr),
        ("log_mapper_userdev.py %s" % datestr, "log_reducer_userdev.py %s" % datestr, "/logs/userdev.%s" % datestr),
        ]

    print "config hadoop"
    filename = targetdir + "/windows2x.log.%s" % runday.strftime("%Y-%m-%d")
    print filename
    #dump 数据库到本地文件
    fp = open(filename, "w")
    db.query("SELECT content FROM interface_logentity where `create` > '%s' and `create` < '%s';" % (runday.strftime("%Y-%m-%d"), (runday + datetime.timedelta(days=1)).strftime("%Y-%m-%d")))
    r = db.store_result()
    n = r.num_rows()
    for i in range(0, n):
        content = r.fetch_row()[0][0]
        fp.write(content + "\n")
    fp.close()

    print "begin clean db"
    sqlexe = '/usr/bin/mysql -u%s -p%s -h%s %s' % (dbuser, dbpass, dbhost, dbname)
    os.popen('echo "DELETE FROM interface_logmeta WHERE date=\'%s\';" | %s' % (runday.isoformat(), sqlexe))
    os.popen('echo "DELETE FROM interface_devicelogentity WHERE date=\'%s\';" | %s' % (runday.isoformat(), sqlexe))
    os.popen('echo "DELETE FROM interface_userdevicelogentity WHERE date=\'%s\';" | %s' % (runday.isoformat(), sqlexe))
    os.popen('echo "DELETE FROM interface_installedapplogentity WHERE date=\'%s\';" | %s' % (runday.isoformat(), sqlexe))

    print "begin hadoop"
    for map, red, output in jobs:
        cmd = "cat %s | /usr/local/bin/python2.7 %s%s | /usr/local/bin/python2.7 %s%s | %s" % \
              (filename, jobpath, map, jobpath, red, sqlexe  )
        print cmd
        os.popen(cmd)
    if remove_logs:
        cmd = "rm -f %s.*" % (filename,)
        os.popen(cmd)
    print "hadoop over"

   
    runday += datetime.timedelta(days=1)


