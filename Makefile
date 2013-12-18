all: runserver

TEST_APPS=mgr statistics
PORT=11111

runserver:
	nohup ./manage.py runserver $(PORT) &

test:
	./manage.py test $(TEST_APPS) --settings=suning.settings_test

rebuild_db:
	./rebuild_db.sh

collectstatic:
	./manage.py collectstatic

restart_nginx:
	/etc/init.d/nginx restart

deploy_static: collectstatic restart_nginx

.PHONY: runserver test rebuild_db collectstatic restart_nginx deploy_static


