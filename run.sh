source ./eagle-python/bin/activate
(
  cd eagleproject
  python ./manage.py migrate
  python ./manage.py runserver
)