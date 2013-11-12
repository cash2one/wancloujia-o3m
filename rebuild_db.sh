#!/bin/bash

mysql -u root -p < replace_db.sql && 
./manage.py syncdb --noinput && 
./manage.py ensure_groups_and_permissions && 
./manage.py set_root root suning
