#!/bin/sh
python manage.py update_database en
python manage.py update_database cn
python manage.py update_database jp
python manage.py migrate
python manage.py collectstatic --no-input
touch rongdjango/wsgi.py
python manage.py runserver