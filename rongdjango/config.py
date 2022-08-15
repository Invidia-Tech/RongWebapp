import os
import json

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
DATABASE_ENGINE = 'django.db.backends.postgresql'
DATABASE_HOST = os.environ['DB_HOST']
DATABASE_PORT = os.environ['DB_PORT']
DATABASE_DB = os.environ['DB_NAME']
DATABASE_USER = os.environ['DB_USER']
DATABASE_PASSWORD = os.environ['DB_PASSWORD']
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = json.loads(os.environ['WEB_ALLOWED_HOSTS'])
DISCORD_CLIENT_ID = os.environ['DISCORD_CLIENT_ID']
DISCORD_CLIENT_SECRET = os.environ['DISCORD_CLIENT_SECRET']
DISCORD_BASE_URL = 'https://discord.com/api'
DISCORD_OAUTH_URL = DISCORD_BASE_URL + '/oauth2/authorize'
DISCORD_TOKEN_URL = DISCORD_BASE_URL + '/oauth2/token'
STATIC_ROOT = '/var/www/rongwebapp/static/'
EXTRA_APPS = ('mod_wsgi.server',)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
