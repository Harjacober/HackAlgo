from flask import g
import os
from random import randint
from time import time


class Task:
    PossibelTasksState=["initialize","inqueue","running","finished","result"]
    def __init__(self,lang,content,person_email,problem_id):
        self.state="initialize"
        self.lang=lang
        self.content=content
        self.person_email=person_email
        self.problem_id=problem_id
    def __enter__(self):
        self.folder=self.resolveFolder(self.lang)
        self.filename=self.randomFilename()
        self.file=open("/tmp/{}/{}".format(self.folder,self.filename),"w")

    def __exit__(self):
        self.file.close()
        os.remove("/tmp/{}/{}".format(self.folder,self.filename))
    
    def resolveFolder(self,lang):
        #python is py,java is java e.t.c.This function exist if need be resolve the name later
        return lang
    def randomFilename(self):
        return self.person_email+"{}{}".format(time(),hash(self))
    def status(self):
        pass
    def run(self):
        pass

        
