#!/bin/bash

if [ ! -f "backend/config.py" ]; then
    echo "config.py not found. Use the default config instead"
    cp backend/config.example.py backend/config.py
fi

cd cobra_wrapper/remote
/wait.sh -t 120 rabbitmq:5672
celery worker -l info -A cobra_computation -Q cobra_feeds &
cd ..
celery worker -l info -A backend -Q cobra_results &
cd ..

/wait.sh -t 120 mysql:3306 -- python manage.py runserver 0:8000 --noreload
