# encoding: utf-8
#Full path and name to your csv file
csv_filepathname = '/data/looyu/store.csv'
#Full path to your django project directory
djangoproject_home = '/data/looyu/suning/'
import logging
import sys,os
sys.path.append(djangoproject_home)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from mgr.models import Company,Region,Store

import csv
import traceback
logger = logging.getLogger('import_data')

def _verify(index,row):
    if len(row) == 0:
        logger.info("空数据")
        return False
    if row[0].upper() == 'CODE':
        logger.info('开始插入门店数据~')
        return True
    else:
        logger.info('开始第' + str(index) + '行数据的输入')
        if row[0]=='' or row[1]=='' or row[2]=='': 
            logger.info('数据不完全')
            return False
        if Store.objects.filter(code=row[0]).exists() or Store.objects.filter(name=row[2]).exists():
            logger.info('门店编码或者公司名称重复')
            return False
        return True

def _get_Company(storeName):
    #有就查没有就跳过
    if Company.objects.filter(name=unicode(storeName,"utf-8")).exists():
        logger.info('查到公司')
        return Company.objects.get(name=unicode(storeName,"utf-8")).pk
    else:
        logger.info(storeName)
        logger.info(unicode(storeName,"utf-8"))
        logger.info('没有查到公司')
        return -1
try:
    dataReader = csv.reader(open(csv_filepathname),delimiter=',',quotechar='"')
    for index, row in enumerate(dataReader):
        if _verify(index,row) and index != 0:
            store = Store()
            store.code = row[0]
            store.name = row[2]
            company = _get_Company(row[1])
            if company == -1:
                pass
            else:
                store.company_id=company
                store.save()
        else:
            pass
except Exception,e:
    print'出错了'
    exstr = traceback.format_exc()
    print exstr



        
        
    
        
        
        
