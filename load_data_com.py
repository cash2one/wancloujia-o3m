
# encoding: utf-8
#Full path and name to your csv file
csv_filepathname = '/data/looyu/test_company.csv'
#Full path to your django project directory
djangoproject_home = '/data/looyu/suning/'
import logging
import sys,os
sys.path.append(djangoproject_home)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from mgr.models import Company,Region

import csv
import traceback
_DEFAULT_PASSWORD= '123456'
logger = logging.getLogger('import_data')

def _verify(index,row):
    if len(row) == 0:
        logger.info("空数据")
        return False
    if row[0].upper() == 'CODE':
        logger.info('开始插入公司数据~')
        return True
    else:
        logger.info('开始第' + str(index) + '行数据的输入')
        if row[0]=='' or row[1]=='' or row[2]=='': 
            logger.info('数据不完全')
            return False
        if Company.objects.filter(code=row[0]).exists() or Company.objects.filter(name=row[2]).exists():
            logger.info('公司编码或者公司名称重复')
            return False
        return True

def _get_region(regionName):
    #有就查没有就添加吧
    if Region.objects.filter(name=unicode(regionName,"utf-8")).exists():
        logger.info('查到大区')
        return Region.objects.get(name=unicode(regionName,"utf-8")).pk
    else:
        region = Region.objects.create(name=unicode(regionName,"utf-8"))
        logger.info('创建新大区')
        return region.pk
try:
    dataReader = csv.reader(open(csv_filepathname),delimiter=',',quotechar='"')
    for index, row in enumerate(dataReader):
        if _verify(index,row) and index != 0:
            company = Company()
            company.code = row[0]
            company.name = row[2]
            company.region_id = _get_region(row[1])
            company.save()
        else:
            pass
except Exception,e:
    print'出错了'
    exstr = traceback.format_exc()
    print exstr



        
        
    
        
        
        
