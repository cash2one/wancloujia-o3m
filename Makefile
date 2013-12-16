all: runserver

TEST_APPS=mgr statistics
PORT=11112

runserver:
	nohup ./manage.py runserver $(PORT) &

test:
	./manage.py test $(TEST_APPS) --settings=suning.settings_test

rebuild_db:
	./rebuild_db.sh

collectstatic:
	./manage.py collectstatic

.PHONY: runserver test rebuild_db collectstatic

