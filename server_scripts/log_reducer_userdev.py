#!/usr/bin/env python
dbhost = 'localhost'
dbport = 3306
dbuser = 'root'
dbpass = 'funtalkwdj'
dbname = 'funtalk'
debug = False

import _mysql
import sys
import HTMLParser
import json

db = _mysql.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbname)


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
	db.query("SELECT mgr_employee.staff_ptr_id, mgr_employee.organization_id, auth_user.username FROM mgr_employee, auth_user WHERE mgr_employee.staff_ptr_id = auth_user.id;")
	r = db.store_result()
	n = r.num_rows()
	for i in range(0, n):
		row = r.fetch_row()
		uid = row[0][0]
		oid = row[0][1]
		name = row[0][2]
		acc[uid] = (oid, name)
	return acc

def read_app():
	acc = dict()
	db.query("SELECT id, package, name, popularize FROM app_app;")
	r = db.store_result()
	n = r.num_rows()
	for i in range(0, n):
		row = r.fetch_row()
		id = row[0][0]
		pkg = row[0][1]
		name = row[0][2]
		pop = row[0][3]
		acc[str(id)] = (pkg, name, pop)
	return acc

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

staffs = read_staff()
regions = read_region()
companys = read_company()
stores = read_store()
map = map_staff(staffs, regions, companys, stores)
apps = read_app()
#print map
import datetime
lastDay = datetime.date.today() - datetime.timedelta(days=0 if debug else 1)

existed = set()
existed2 = set()
#db.query("DELETE FROM interface_userdevicelogentity WHERE date ='%s';" % (lastDay.isoformat()))
#r = db.store_result()
for line in sys.stdin:
	#print line
	try:
		user, did, appid = line.strip().split(',')
		if (user, did,) in existed:
			print "UPDATE interface_userdevicelogentity SET popularizeAppCount = popularizeAppCount + %s , appCount = appCount + 1 WHERE date = '%s' AND uid =%s;" \
				% (apps[appid][2], lastDay.isoformat(), map[user][0])
		else:
			if user in existed2:
				print "UPDATE interface_userdevicelogentity SET deviceCount = deviceCount + 1, popularizeAppCount = popularizeAppCount + %s , appCount = appCount + 1 WHERE date = '%s' AND uid =%s;" \
					% (apps[appid][2], lastDay.isoformat(), map[user][0])
			else:
				print "INSERT INTO interface_userdevicelogentity(date, region, company, store, uid , deviceCount , popularizeAppCount, appCount, appPkg) VALUES('%s', %s , %s, %s, %s, %s, %s, %s, '%s');" \
					% ( lastDay.isoformat(), map[user][1], map[user][2], map[user][3], map[user][0], '1', apps[appid][2] , '1', apps[appid][0])
				existed2.add(user)
			existed.add((user, did,))
	except:
		pass
