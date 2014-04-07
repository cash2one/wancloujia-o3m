#coding: utf-8
print "begin script"
# config begin
#debug = True表示把现在(今天)的日志进行收集,False表示拿昨天的日志进行收集
#另外的 debug =False会在处理动作的最后删除本机原始的日志
debug = True  # True->windows2x.log, false->windows2x.log.<lastday>
#server_id是一个用来标识上传到hdfs的本机已处理好的日志的id,免得跟其他节点上传的日志名字重复
server_id = "1"
#logdir是log产生的目录位置
logdir = "/data/tianyin.proj/tianyin/logs"
#tmpdir是用来指定在本机过滤日志的地方(目录)
tmpdir = "/data/tianyin.proj/tianyin/logs"
remove_old_log = False
#最终放置此节点log的地方
targetdir = "/data/logs"
# config over
###################################################
###################################################
file = logdir + "/windows2x.log"
file_tmp = tmpdir + "/windows2x.tmp.log"

print "begin re"
import re
print "begin json"
import json
print "begin os"
import os
print "begin datetime"
import datetime

print "立即截断当前日志"
###################################
# 立即截断当前日志
###################################
os.popen('curl -d "" http://localhost:13000/muce/signal')


print "打开日志和临时文件"
###################################
# 打开日志和临时文件
###################################
if debug:
    pass
else:
	lastDay = datetime.date.today() - datetime.timedelta(days=1)
	file = logdir + "/windows2x.log.%s" % (lastDay.isoformat(),)

headerRE = re.compile(r"^\[windows2x\](?P<header>.*)")
contentRE = re.compile(r"^tianyin\.install\.success\s(?P<content>[^\t]+)\s\d+")
#contentRE2 = re.compile(r"^tianyin\.install\s(?P<content>[^\t]+)\s\d+")
contentRE2 = re.compile(r"^(?P<content>[^\t]+)\s(?P<content2>[^\s]+)\s\d+")
fp = open(file)
fp2 = open(file_tmp, "w")


print "正则匹配出我们需要处理的日志项到临时文件里面去"
###################################
# 正则匹配出我们需要处理的日志项到临时文件里面去
###################################
def remap_log_content(content):
    result = re.match(contentRE, content)
    result2 = re.match(contentRE2, content)
    is_success = False
    if result:
    	resultdict = result.groupdict()
        is_success = True
    elif result2:
        resultdict = result2.groupdict()
    else:
    	resultdict = None
    if resultdict and "content" in resultdict and "content2" in resultdict:
    	j =json.loads(resultdict['content'])
        k = json.loads(resultdict['content2'])
    	j["log_type"] = 'success' if j['event'] == 'tianyin.install.success' else 'install'
        j['deviceId'] = k['deviceId']
    	encodedjson = json.dumps(j)
    	fp2.write(encodedjson + "\n")

for i in fp.readlines():
    try:
        result = re.match(headerRE, i)
        if result:
            resultdict = result.groupdict()
        else:
            resultdict = None
        if resultdict and "header" in resultdict:
            pass #new log header
        else:
            if i.index('install') == 0:
                pass
            remap_log_content(i)
    except:
        pass

fp.close()
fp2.close()

print "本机结果上传到hdfs"
###################################
# 本机结果上传到hdfs  # fix nfs
###################################
if debug == True:
    lastDay = datetime.date.today()
else:
    lastDay = datetime.date.today() - datetime.timedelta(days=1)
file_dst_hdfs = "windows2x.log.%s" % (lastDay.isoformat(),)

app_cmd = r'cp %s %s/%s.%s' % \
    (file_tmp, targetdir, file_dst_hdfs, server_id,)
os.popen(app_cmd)
os.remove(file_tmp)
print "删除本机原有的日志文件"
###################################
# 删除本机原有的日志文件
###################################
if remove_old_log:
    os.remove(file)

