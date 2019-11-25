"""
This class holds runnng tasks and can provide the status of each 
"""
from os import getcwd
from bson.objectid import ObjectId

class Queue:
    tasks={}
    idsAvailable=[]

    def add(self,id,task):
        if id in Queue.tasks:
            print("WARN: id in task")
        Queue.tasks[id]=task
        Queue.tasks[id].start()


    def getById(self,id):
        return Queue.tasks[id] if self.checkForID(id) else None

    def status(self,id):
        if id not in Queue.tasks:
            return "Task not found in queue"
        return  Queue.tasks[id].status

    def done(self,id):
        if id not in Queue.tasks:
            return "Task not found in queue"
        Queue.tasks.pop(id)
        Queue.idsAvailable.append(id)
        Print(" Removed ID {}".format(id))

    def checkForID(self,id):
        return id in Queue.tasks

    @classmethod
    def generateID(self):
        if Queue.idsAvailable:
            return Queue.idsAvailable.pop()
        
        return str(ObjectId())



#This is the global queue all task will be stored here . Sorry
#if you import this entire module you calling this to yourname space
queue=Queue()

