import datetime
from platform import system

JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=20)
JWT_SECRET_KEY = "Q24JKjhdbjsJNBKsukdsnkjdsJWjsdnkjdsbdkjn"  #if you have a cat/dog allow it to type this. more random
TESTING = True  # During development use this
REDIS_HOST="redis" if system()=='Linux' else 'localhost'
CELERY_BROKER_URL= 'redis://{}:6379/0'.format(REDIS_HOST)
CELERY_RESULT_BACKEND='redis://{}:6379/0'.format(REDIS_HOST)
CELERY_TRACK_STARTED=True
CELERY_IMPORTS = ("app","coderunner.celerytasks")