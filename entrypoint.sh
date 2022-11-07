#!/bin/sh

set -e
  
# Login for user (`-U`) and once logged in execute quit ( `-c \q` )
# If we can not login sleep for 1 sec
until PGPASSWORD=origin psql -h "ousda-db" -U "ousda" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
  
>&2 echo "Postgres is up - executing migrations"

# Migrate
python manage.py migrate
echo "Migrations complete, starting server"

sleep 3

exec "$@"
