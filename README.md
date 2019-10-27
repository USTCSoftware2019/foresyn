# Foresyn
[![Build Status](https://travis-ci.com/USTCSoftware2019/foresyn.svg?branch=master)](https://travis-ci.com/USTCSoftware2019/foresyn)

iGEM project by USTC Software 2019. 

## Installation

Assuming that you are using Debian Buster and Python 3.7.

### Initialization

1. Install MySQL (or MariaDB), PostgreSQL and RabbitMQ.

   ```shell
   $ apt update && apt upgrade
   $ apt install mariadb-server rabbitmq-server p7zip-full python3-psycopg2 libpq-dev postgresql postgresql-contrib
   $ mysql_secure_installation  # setting mysql/mariadb
   $ mysql  
   (and then type `GRANT ALL ON *.* TO 'set_your_admin_user_name_here'@'localhost' IDENTIFIED BY 'set_your_admin_password_here' WITH GRANT OPTION;` and `FLUSH PRIVILEGES;` inside, to let our project access mysql database)
   ```

2. Use `git` to clone this project to your computer.

3. Enter into project folder, create a Python virtual environment by:

   ```shell
   $ python3 -m venv venv
   $ source venv/bin/activate
   (venv) $ pip install wheel  # to prevent installation failure
   (venv) $ pip install -r requirements.txt
   (venv) $ sed -i '34 s/^/#/; 35 s/^/#/; 36 s/^/#/' venv/lib/python3.7/site-packages/django/db/backends/mysql/base.py && sed -i 's/.decode(errors/.encode(errors/g' venv/lib/python3.7/site-packages/django/db/backends/mysql/operations.py
   ```

4. Write project configuration. Copy `backend/backend/config.example.py` to `backend/backend/config.py`, and modify according to your environment.

5. Create and migrate database, and load SQL data by using `mysql`

   ```shell
   $ echo "CREATE DATABASE igem_backend CHARACTER SET utf8 COLLATE utf8_bin;" | sudo mysql # Create database with name "igem_backend" for mysql
   (venv) $ python manage.py migrate
   $ echo "SET GLOBAL max_allowed_packet=107374182;" | sudo mysql # ensure the large dump imported successfully
   $ sudo mysql < data/all.sql
   $ sudo su postgres -c "echo \"CREATE DATABASE igem_backend\" | psql" # Create database with name "igem_backend" for PostgreSQL
   $ sudo su postgres -c "echo \"CREATE USER igem WITH PASSWORD 'igem';\" | psql" # Create a new user "igem" with password "igem" for PostgreSQL
   ```

6. Import data to PostgreSQL by typing:

   ```shell
   (venv) $ python manage.py migrate_to_psql
   ```


### Run This Project

1. Load Celery computation tasks.

   ```shell
   (venv) $ cd backend/cobra_wrapper/remote/
   (venv) $ env PYTHONOPTIMIZE=1 celery worker -l info -A cobra_computation -Q cobra_feeds
   (a new shell)
   (venv) $ cd backend
   (venv) $ env PYTHONOPTIMIZE=1 celery worker -l info -A backend -Q cobra_results
   ```

2. Run this project.

   ```shell
   (venv) $ python manage.py runserver
   ```

   