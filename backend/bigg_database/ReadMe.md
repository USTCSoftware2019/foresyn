### MySQL Database

**Don't import the sql file directly into an existing database whose character set is default, latin1.**

Create database

```
CREATE DATABASE igem_backend CHARACTER SET utf8 COLLATE utf8_bin;
```

### Temporary solution for pymysql

In ```site-packages\django\db\backends\mysql\base.py#34```

Comment #34, #35, #36

```
version = Database.version_info
if version < (1, 3, 13):
    raise ImproperlyConfigured('mysqlclient 1.3.13 or newer is required; you have %s.' % Database.__version__)
```

In ```site-packages\django\db\backends\mysql\operations.py#146```

Change ```query = query.decode(errors='replace')``` to ```query = query.encode(errors='replace')```



### haystack and elasticsearch

Due to the limit from the haystack, the version of elasticsearch must lower than 3.0.0

For this project, we choose elasticsearch 2.4.6

Download: [elasticsearch-2-4-6](https://www.elastic.co/cn/downloads/past-releases/elasticsearch-2-4-6)

#### Usage (Ubuntu): 

- Install: ```sudo dpkg elasticsearch-2.4.6.deb```

- Start serive: ```sudo service elasticsearch start```

> To start elasticsearch, java 8 is required
>
> Install: ```sudo apt install openjdk-8-jre-headless```

install elasticsearch-dsl using ```pip3 install "elsaticsearch>=2.0.0,<3.0.0"```(Included in requirements.txt)

- Build indexes

Rebuild the index (also build index for the first time)

```python3 ./manage.py rebuild_index```

Update the index

```python3 ./manage.py update_index```