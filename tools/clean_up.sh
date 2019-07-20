
cd ../bigg_database

echo rm migrations
rm -r ./bigg_database/migrations

echo rm db.sqlite3
rm db.sqlite3

echo migrate again
python3 ./manage.py makemigrations bigg_database
python3 ./manage.py migrate