# encoding: utf-8
#Full path and name to your csv file
csv_filepathname = '/data/looyu/user.csv'
#Full path to your django project directory
djangoproject_home = '/data/looyu/suning/'
import logging
import sys,os
sys.path.append(djangoproject_home)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from mgr.models import Employee, Organization, Group
from django.contrib.auth.models import User, Group, Permission

import csv
import traceback
_DEFAULT_PASSWORD= '123456'
logger = logging.getLogger('import_data')

usernames = {}
orgs = {}
groups = {}

for i in User.objects.all():
    usernames[i.username] = True
for i in Organization.objects.all():
    orgs[i.cast().name] = i.pk
for i in Group.objects.all():
    groups[i.name] = i.name 
def _verify(index,row):
    if len(row) == 0:
        logger.info("空数据")
        return False
    if row[0].upper() == 'USERNAME':
        logger.info('开始插入数据~')
        return True
    else:
        logger.info('开始第' + str(index) + '行数据的输入')
        if row[0]=='' or row[1]=='' or row[2]=='' or row[3]=='' or row[4]=='':
            logger.info('数据不完全')
            return False
        #if User.objects.filter(username=row[0]).exists():
        if usernames.has_key(row[0]):
            logger.info('username重复')
            return False
        return True
             

def _get_org(orgName):
    #orgs = Organization.objects.all()
    #for org in orgs:
    #    if unicode(orgName,"utf-8") == org.cast().name:
    #        return org.pk
    if orgs.has_key(unicode(orgName,"utf-8")):
        return orgs[unicode(orgName,"utf-8")]
    logger.info('对不起没有该机构~')
    return -1

try:
    dataReader = csv.reader(open(csv_filepathname),delimiter=',',quotechar='"')
    for index, row in enumerate(dataReader):
        if _verify(index,row) and index != 0:
            user = Employee()
            password = _DEFAULT_PASSWORD
            user.set_password(password)
            user.username=row[0]
            user.realname=row[1]
            organization=row[2]
            if _get_org(organization) == -1:
                continue
            else:
                user.organization = Organization.objects.get(pk=_get_org(organization))
            user.phone=row[3]
            user.email=row[4]
            user.tel=row[5]
            user.introduce=row[6]
            user.save()
            group = row[7]
            user.groups= groups[group] if groups.has_key(group) else ""   #Group.objects.filter(name=group)
            user.save()
            usernames[row[0]] = True
            logger.info(str(index)+'行数据已插入完毕')
        else:
            pass
except Exception,e:
    print'出错了'
    exstr = traceback.format_exc()
    print exstr



        
        
    
        
        
        
