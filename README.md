# Foresyn
[![Build Status](https://travis-ci.com/taoky/backend.svg?token=9jooK4Qfof8h4FFgpnEK&branch=master)](https://travis-ci.com/taoky/backend)

iGEM project by USTC Software 2019. 

## Installation

Assuming that you are using Debian Buster.

1. Install MySQL (or MariaDB), RabbitMQ and ElasticSearch 2.4.6.

   ```shell
   # apt install mariadb-server rabbitmq-server
   # apt install apt-transport-https ca-certificates wget dirmngr gnupg software-properties-common  # setting up openjdk8, as buster no longer provides it
   # wget -qO - https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | apt-key add -
   # add-apt-repository --yes https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/
   # apt update
   # apt install adoptopenjdk-8-hotspot
   # wget https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/deb/elasticsearch/2.4.6/elasticsearch-2.4.6.deb
   # dpkg --install elasticsearch-2.4.6.deb
   # mysql_secure_installation  # setting mysql/mariadb
   ```

2. Use `git` to clone this project to your computer.

3. Enter into project folder, create a Python virtual environment by:

   ```shell
   $ python3 -m venv venv
   $ source venv/bin/activate
   (venv) $ pip install wheel  # to prevent installation failure
   ```

4. Write project configuration. Copy `backend/backend/config.example.py` to `backend/backend/config.py`, and modify according to your environment.

5. Migrate database, and load SQL data by using `mysql`

   ```shell
   (venv) $ python manage.py migrate
   $ sudo mysql < data/all.sql
   ```

6. aaa