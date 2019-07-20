@echo off

cd ../bigg_database

echo Deleting db.sqlite3
del db.sqlite3

echo rm migrations files
rd /S /Q bigg_database\migrations

echo Migrate again
py manage.py makemigrations bigg_database
py manage.py migrate