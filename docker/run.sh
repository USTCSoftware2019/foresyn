#!/bin/bash
/wait.sh -t 120 elasticsearch:9200 -- python manage.py rebuild_index --noinput
/wait.sh -t 120 mysql:3306 -- python manage.py runserver 0:8000
