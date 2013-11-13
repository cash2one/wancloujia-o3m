#!/bin/bash

echo "clear database" &&
mysql -u root -p < replace_db.sql && 

echo "synchroize db" &&
./manage.py syncdb --noinput --traceback && 

echo "ensure groups and permissions" &&
./manage.py ensure_groups_and_permissions --traceback && 

echo "create root user" &&
./manage.py set_root root suning --traceback
