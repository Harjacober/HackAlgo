import datetime
from platform import system

JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=20)
JWT_SECRET_KEY = "Q24JKjhdbjsJNBKsukdsnkjdsJWjsdnkjdsbdkjn"  #if you have a cat/dog allow it to type this. more random
TESTING = False  # During development use this
CELERY_TEST = False
REDIS_HOST="redis" if system()=='Linux' else 'localhost'
CELERY_BROKER_URL= 'redis://{}:6379/0'.format(REDIS_HOST)
CELERY_RESULT_BACKEND='redis://{}:6379/0'.format(REDIS_HOST)
CELERY_TRACK_STARTED=True
CELERY_IMPORTS = ("app","api.access.contest")
MAIL_SERVER="smtp.gmail.com"
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME="hackalgodevs@gmail.com"
MAIL_PASSWORD= "H@ck@lg0911"

