all: run

TEST_APPS:=mgr statistics
PORT:=13010
DEBUG_PORT:=11111

run:
	nohup ./manage.py runserver $(PORT) &

debug:
	nohup ./manage.py runserver $(DEBUG_PORT) & 

test:
	./manage.py test $(TEST_APPS) --settings=suning.settings_test

plugin: 
	zip assets/wandoujia.zip wandoujia/*

rebuild_db:
	./rebuild_db.sh

collectstatic:
	./manage.py collectstatic --noinput

restart_nginx:
	sudo /sbin/service nginx restart

deploy_static: collectstatic restart_nginx

.PHONY: run \
		debug \
		test \
		rebuild_db \
		collectstatic \
		restart_nginx \
		plugin \
		deploy_static

