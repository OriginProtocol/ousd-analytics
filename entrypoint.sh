#!/bin/bash
# To be used by docker as an entrypoint
set -e

python manage.py migrate
python manage.py runserver
