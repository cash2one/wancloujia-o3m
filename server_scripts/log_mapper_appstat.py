#!/usr/bin/env python
dbhost = 'dev-node1.limijiaoyin.com'
dbport = 3306
dbuser = 'root'
dbpass = 'nameLR9969'
dbname = 'suning'

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

import datetime
import HTMLParser
lastDay = datetime.date.today() - datetime.timedelta(days=1)

existed = set()

for line in sys.stdin:
	try:
		j =json.loads(line)
		appid = _mysql.escape_string(j["app"].strip())
		brand = _mysql.escape_string(j["brand"].strip().upper())
		did = _mysql.escape_string(j["deviceId"].strip().upper())
		model = _mysql.escape_string(j["model"].strip().upper())
		pkg = _mysql.escape_string(j["package"].strip())
		user = _mysql.escape_string(str(j["user"]).strip())
		print "%s,%s" % (user, appid)
	except:
		pass