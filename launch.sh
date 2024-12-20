#!/bin/sh
cp rongdjango/config.docker.py rongdjango/config.py || true
rm rongdjango/config.docker.py || true
python manage.py update_database en
python manage.py update_database cn
python manage.py update_database jp
python manage.py migrate
python manage.py populate_aliases
python manage.py collectstatic --no-input
touch rongdjango/wsgi.py
python manage.py runmodwsgi --setup-only \
    --user www-data --group www-data \
    --server-root=/etc/mod_wsgi-rongwebapp
/etc/mod_wsgi-rongwebapp/apachectl start
tail -f /etc/mod_wsgi-rongwebapp/error_log