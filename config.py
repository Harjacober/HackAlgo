import datetime
from platform import system
import os


JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=20)
JWT_SECRET_KEY = "Q24JKjhdbjsJNBKsukdsnkjdsJWjsdnkjdsbdkjn"  #if you have a cat/dog allow it to type this. more random
TESTING = os.environ.get("TESTING","1")=="1"  # During development use this
CELERY_TEST = False
REDIS_HOST="redis" if system()=='Linux' else 'localhost'
CELERY_BROKER_URL= 'redis://{}:6379/0'.format(REDIS_HOST)
CELERY_RESULT_BACKEND='redis://{}:6379/0'.format(REDIS_HOST)
CELERY_TRACK_STARTED=True
CELERY_IMPORTS = ("app","api.access.contest")
MAIL_SERVER="smtp.live.com"
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME="codegee@outlook.com"
MAIL_PASSWORD= "CodeAndGee"
SECRET_KEY = b'7c56f3a987c603a9816b44c96e221ff86f7b7a6196062a804843fad8e204240620c40f7e2ca0c240e22d19728dee84fc7c06'
HOST = "http://localhost:9000" if TESTING else "http://40.77.105.238:5000"
FRONT_END_HOST = "http://localhost:8080" #definately need to change

