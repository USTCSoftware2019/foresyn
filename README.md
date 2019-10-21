# Foresyn
[![Build Status](https://travis-ci.com/taoky/backend.svg?token=9jooK4Qfof8h4FFgpnEK&branch=master)](https://travis-ci.com/taoky/backend)

iGEM project by USTC Software 2019. 

## Installation

Assuming that you are using Debian Buster and Python 3.7.

1. Install MySQL (or MariaDB), RabbitMQ and ElasticSearch 2.4.6.

   ```shell
   # apt install mariadb-server rabbitmq-server p7zip-full
   # apt install apt-transport-https ca-certificates wget dirmngr gnupg software-properties-common  # setting up openjdk8, as buster no longer provides it
   # wget -qO - https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | apt-key add -
   # add-apt-repository --yes https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/
   # apt update
   # apt install adoptopenjdk-8-hotspot
   # wget https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/deb/elasticsearch/2.4.6/elasticsearch-2.4.6.deb
   # dpkg --install elasticsearch-2.4.6.deb
   # mysql_secure_installation  # setting mysql/mariadb
   # mysql  
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
   $ echo "CREATE DATABASE igem_backend CHARACTER SET utf8 COLLATE utf8_bin;" | sudo mysql
   (venv) $ python manage.py migrate
   $ sudo mysql
   (and then type `SET GLOBAL max_allowed_packet=107374182;`, to ensure the large dump imported successfully)
   $ sudo mysql < data/all.sql
   ```

6. Initialize ElasticSearch by typing:

   ```shell
   (venv) $ python manage.py rebuild_index
   ```

   