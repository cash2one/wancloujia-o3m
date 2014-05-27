#!/bin/bash

DBNAME=funtalkwdj

sql=$(cat <<-EOF
drop database $DBNAME;
create database $DBNAME;
EOF
)

echo "clear database" && 
echo $sql | mysql --user=root --password=password  &&

echo "synchroize db" &&
./manage.py syncdb --noinput --traceback &&

echo "ensure groups and permissions" &&
./manage.py ensure_groups_and_permissions --traceback &&

echo "create root user" &&
./manage.py set_root root funtalk --traceback

