SECRET_KEY = "This is USTC-Software 2019, replace this string with os.urandom(1024) or other secret string"
DEBUG = False

USE_ELASTICSEARCH = True
ELASTICSEARCH_HOST = "127.0.0.1"

USE_MYSQL = True
MYSQL_HOST = "127.0.0.1"
MYSQL_USER = "root"
MYSQL_PASSWORD = "mysql_pwd"
MYSQL_PORT = 3306

CELERY_BROKER_URL = 'amqp://guest:guest@localhost//'

USE_EMAIL = False
# if USE_EMAIL is False, email will output on console
EMAIL_HOST = None
EMAIL_PORT = 587
EMAIL_HOST_USER = "username"
EMAIL_HOST_PASSWORD = "password"
DEFAULT_FROM_EMAIL = "no-reply@mail.foresyn.tech"

STATIC_ROOT = "/var/www/static/"
# if you are just testing, set it to None is ok.
