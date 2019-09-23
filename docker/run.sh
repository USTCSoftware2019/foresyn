#!/bin/bash
/wait.sh -t 120 elasticsearch:9200 -- python manage.py update_index --noinput
cd cobra_wrapper/remote
/wait.sh -t 120 rabbitmq:5672
celery worker -l info -A cobra_computation -Q cobra_feeds &
cd ..
celery worker -l info -A backend -Q cobra_results &
cd ..
/wait.sh -t 120 mysql:3306 -- python manage.py runserver 0:8000
