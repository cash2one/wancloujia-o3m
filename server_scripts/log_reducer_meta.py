#!/usr/bin/env python
#coding: utf-8
dbhost = 'dev-node1.limijiaoyin.com'
dbport = 3306
dbuser = 'root'
dbpass = 'nameLR9969'
dbname = 'tianyin'

import sys  
reload(sys)  
sys.setdefaultencoding('utf-8')
import _mysql
import sys
import HTMLParser
import json
import urllib

db = _mysql.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)
db.query("SET NAMES utf8")
db.query("SET CHARACTER_SET_CLIENT=utf8")
db.query("SET CHARACTER_SET_RESULTS=utf8")


class LogItem(object):
    def __init__(self, user, did, brand, model, subj, obj):
        super(LogItem, self).__init__()
        self.user  = user
        self.did   = did
        self.brand = brand
        self.model = model
        self.subj  = subj
        self.obj   = obj
    def __cmp__(self, right):
        if right == None or not isinstance(right,LogItem):
            return 1
        elif self.user == right.user:
            if self.did == right.did:
                if self.brand == right.brand:
                    if self.model == right.model:
                        if self.subj == right.subj:
                            return 0
                        else:
                            return self.subj == right.subj
                    else:
                        return self.model == right.model
                else:
                    return self.brand == right.brand
            else:
                return self.did == right.did
        else:
            return self.user == right.user
        
def read_subj():
    acc = {}
    db.query("SELECT id, name FROM app_subject;")
    r = db.store_result()
    n = r.num_rows()
    for i in range(0,n):
        row = r.fetch_row()
        id = int(row[0][0])
        name = row[0][1]
        acc[id] = urllib.unquote(name)
    return acc

def read_region():
    acc = set()
    db.query("SELECT organization_ptr_id FROM mgr_region;")
    r = db.store_result()
    n = r.num_rows()
    for i in range(0, n):
        oid = r.fetch_row()[0][0]
        acc.add(oid)
    return acc


def read_company():
    acc = dict()
    db.query("SELECT organization_ptr_id, region_id FROM mgr_company;")
    r = db.store_result()
    n = r.num_rows()
    for i in range(0, n):
        row = r.fetch_row()
        oid = row[0][0]
        rid = row[0][1]
        acc[oid] = rid
    return acc


def read_store():
    acc = dict()
    db.query("SELECT organization_ptr_id, company_id FROM mgr_store;")
    r = db.store_result()
    n = r.num_rows()
    for i in range(0, n):
        row = r.fetch_row()
        oid = row[0][0]
        cid = row[0][1]
        acc[oid] = cid
    return acc


def read_staff():
    acc = dict()
    db.query(
        "SELECT mgr_employee.staff_ptr_id, mgr_employee.organization_id, auth_user.username FROM mgr_employee, auth_user WHERE mgr_employee.staff_ptr_id = auth_user.id;")
    r = db.store_result()
    n = r.num_rows()
    for i in range(0, n):
        row = r.fetch_row()
        uid = row[0][0]
        oid = row[0][1]
        name = row[0][2]
        acc[uid] = (oid, name)
    return acc


# def read_app():
#     acc = dict()
#     db.query("SELECT id, package, name, popularize FROM app_app;")
#     r = db.store_result()
#     n = r.num_rows()
#     for i in range(0, n):
#         row = r.fetch_row()
#         id = row[0][0]
#         pkg = row[0][1]
#         name = row[0][2]
#         pop = row[0][3]
#         acc[str(id)] = (pkg, name, pop)
#     return acc


def map_staff(staffs, regions, companys, stores):
    acc = dict()
    for uid in staffs:
        try:
            oid, name = staffs[uid]
            name = str(name)
            if oid in stores:
                store = oid
                company = stores[oid]
                region = companys[company]
                acc[name] = (uid, region, company, store)
            elif oid in companys:
                store = "NULL"
                company = oid
                region = companys[company]
                acc[name] = (uid, region, company, store)
            elif oid in regions:
                store = "NULL"
                company = "NULL"
                region = oid
                acc[name] = (uid, region, company, store)
        except:
            pass
    return acc


def read_brand_model():
    acc = set()
    db.query("SELECT brand, model FROM statistics_brandmodel;")
    r = db.store_result()
    n = r.num_rows()
    for i in range(0, n):
        row = r.fetch_row()
        key = (row[0][0], row[0][1])
        acc.add(key)
    return acc

def read_did():
    acc = set()
    db.query("SELECT did FROM statistics_did;")
    r = db.store_result()
    n = r.num_rows()
    for i in range(0, n):
        row = r.fetch_row()
        key = (row[0][0])
        acc.add(key)
    return acc


staffs = read_staff()
regions = read_region()
companys = read_company()
stores = read_store()
#apps = read_app()
map = map_staff(staffs, regions, companys, stores)
brandmodel = read_brand_model()
dids = read_did()
subjects = read_subj()
#print subjects
import datetime
import collections

successes = collections.deque()
installes = dict()
#print map
lastDay = datetime.date.today() - datetime.timedelta(days=0)
for line in sys.stdin:
    try:
        if len(line.strip()) == 0:
            continue
        j = json.loads(line)
        #appid = _mysql.escape_string(j["app"].strip())
        brand = _mysql.escape_string(j["brand"].strip().upper())
        did = _mysql.escape_string(j["deviceId"].strip().upper())[-8:]
        model = _mysql.escape_string(j["model"].strip().upper())
        #pkg = _mysql.escape_string(j["package"].strip())
        user = _mysql.escape_string(str(j["user"]).strip())
        subj = _mysql.escape_string(str(j["subj"]).strip())
        client = _mysql.escape_string(str(j["client"]).strip())
        #succ = _mysql.escape_string(str(j["success"]).strip())
        log_type = _mysql.escape_string(str(j["log_type"]).strip())
        #print "subj:", subj
        logitem = (user,did,brand,model,subj,client,)
        if log_type == 'success':
            successes.append(logitem)
        else:
            installes[logitem] = installes.get(logitem,0) + 1
        if not brand or not model or not did:
            continue
        if (brand, model,) in brandmodel:
            pass
        else:
            print "INSERT INTO statistics_brandmodel(brand, model) VALUES('%s', '%s');" % \
              (brand, model )
            brandmodel.add((brand, model,))
        if did in dids:
            pass
        else:
            print "INSERT INTO statistics_did(did) VALUES('%s');" % \
              (did, )
            dids.add(did)
        # print "INSERT INTO interface_logmeta(date, uid, did, brand, model, subject, installed, client_version) VALUES('%s', '%s', '%s', '%s', '%s', %s, %s, '%s');" % \
        #       ( lastDay.isoformat(), map[user][0], did, brand, model, subj, succ, '1.0.0.0')
    except:
        pass

for i in successes:
    if installes.has_key(i):
        installes[i] = 0 if installes[i] < 2 else installes[i] - 1
    print "INSERT INTO interface_logmeta(date, uid, did, brand, model, subject, installed, client_version) VALUES('%s', '%s', '%s', '%s', '%s', %s, %s, '%s');" % \
              ( lastDay.isoformat(), map[i[0]][0], i[1], i[2], i[3], i[4], '1', i[5])


for i in installes.keys():
    for j in range(installes[i]):
        print "INSERT INTO interface_logmeta(date, uid, did, brand, model, subject, installed, client_version) VALUES('%s', '%s', '%s', '%s', '%s', %s, %s, '%s');" % \
              ( lastDay.isoformat(), map[i[0]][0], i[1], i[2], i[3], i[4], '0', i[5])
