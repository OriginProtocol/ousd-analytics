source ./eagle-python/bin/activate
(
  cd eagleproject
  python3 ./manage.py migrate
  python3 ./manage.py runserver
)