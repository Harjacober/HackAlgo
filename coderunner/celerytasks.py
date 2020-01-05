from celery import Celery
import config


# Initialize Celery
#include should contain app.py module path
celery = Celery("celerytasks" ,broker=config.CELERY_BROKER_URL,include=['home.app'])
celery.config_from_object(config)


class celeryScheduler:
    def __init__(self,timedelta):
        self.duration=timedelta

    def schedule(self,function):
        try:
            function.__call__
        except AttributeError:
            raise AttributeError("object must be a python callable e.g a function")

        @celery.task
        def taskrun():
            function()

        taskrun.apply_async(countdown=self.duration)
        return taskrun


if __name__=="__main__":
    none=None
    import os
    sch=celeryScheduler(10)
    
    def setNone():
        global none
        none="Im no longer none"
        os.environ['NONE']=none 
        print(os.environ['NONE'])

    print(sch.schedule(setNone))

