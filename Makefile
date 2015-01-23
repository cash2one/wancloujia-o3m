all: run

TEST_APPS:=mgr statistics
PORT:=13010
activate_venv=. venv/bin/activate

start-uwsgi:
	$(activate_venv) \
		&& uwsgi --socket 127.0.0.1:$(PORT) \
		--chdir $(shell pwd) \
		--wsgi-file suning/wsgi.py \
		--master \
		--process 4 \
		--daemonize $(shell pwd)/logs/uwsgi.log \
		--pidfile $(shell pwd)/uwsgi.pid  

stop-uwsgi:
	$(activate_venv) && uwsgi --stop uwsgi.pid
  
reload-uwsgi: 
	$(activate_venv) && uwsgi --reload uwsgi.pid

debug:
	nohup ./manage.py runserver 0.0.0.0:$(PORT) &

run:
	nohup ./manage.py runserver $(PORT) &

test:
	./manage.py test $(TEST_APPS) --settings=suning.settings_test

plugin: 
	zip assets/wandoujia.zip wandoujia/*

rebuild_db:
	./rebuild_db.sh

collectstatic:
	$(activate_venv) && ./manage.py collectstatic --noinput

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

