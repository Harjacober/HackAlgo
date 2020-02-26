"""
This class holds runnng tasks and can provide the status of each 
"""

import sched,time
import threading
from os import getcwd
from config import TIMETOEJECT
from bson.objectid import ObjectId
from multiprocessing import Pipe
from collections import deque
from db import redisClient
from redis_collections import SyncableDict, SyncableList,SyncableDeque

TASKDONE="DONE"
TASKSTART="START"
#we probably have a minimum of 8gb ram
#Running each tasks is estimated to take 500mb
#So having minimum of 10 tasks is a good bound
TASKS=10

class Queue(threading.Thread):
    _tasks=SyncableDict(redis=redisClient) 
    _doneTasks=SyncableDict(redis=redisClient)
    _pendingTasks=SyncableDeque(redis=redisClient)
    _idsAvailable=SyncableList(redis=redisClient)

    _s = sched.scheduler(time.time, time.sleep)
    _Alive=True
    _lock=threading.Lock()    

    QueueConnection,ClientConnection=Pipe()
    
    def __init__(self):
        threading.Thread.__init__(self,daemon=True)

    def sync(self):
        if len(Queue._tasks)>0:
            Queue._tasks.sync()
        if len(Queue._doneTasks)>0:
            Queue._doneTasks.sync()
        if len(Queue._pendingTasks)>0:
            Queue._pendingTasks.sync()
        if len(Queue._idsAvailable)>0:
            Queue._idsAvailable.sync()

    def add(self,id,task):
        if id in Queue._tasks:
            print("WARN: id in task")

        #we just want to keep 10 task runing in memory
        if len(Queue._tasks)<=TASKS:
            Queue._tasks[id]=task
            Queue._tasks[id].run(Queue.ClientConnection)
            self.moveTasksToDone(id)
            Queue._s.enter(TIMETOEJECT, 1, self.done,argument=(id,))
        else:
            Queue._pendingTasks.append((id,task))

    def moveTasksToDone(self,id):
        Queue._lock.acquire()
        if id in Queue._tasks:
            Queue._doneTasks[id]=Queue._tasks[id]
            Queue._tasks.pop(id)
        Queue._lock.release()

    def run(self):
        while Queue._Alive:
            try:
                done=Queue.QueueConnection.recv()
                if isinstance(done,list) and len(done)>=2 and done[0]==TASKDONE:
                    self.moveTasksToDone(done[1])
                    if len(Queue._pendingTasks)>0:
                        id,task=Queue._pendingTasks.popleft()
                        Queue._s.enter(0, 1, self.add,argument=(id,task,))
                        Queue._s.enter(TIMETOEJECT, 2, self.done,argument=(id,))   

            except EOFError:
                Queue.QueueConnection,Queue.ClientConnection=Pipe()

            Queue._s.run(blocking=False)
            self.sync()

    def getById(self,id):
        if id in Queue._tasks:
            return Queue._tasks[id]
        if id in Queue._doneTasks:
            return Queue._doneTasks[id]
        for task in Queue._pendingTasks:
            if task.id==id:
                return task

    def status(self,id):
        if id in Queue._tasks:
            return  Queue._tasks[id].status
        if id in Queue._doneTasks:
            return  Queue._doneTasks[id].status
        for task in Queue._pendingTasks:
            if task.id==id:
                return task.status

        return "Task not found in queue"
        

    def done(self,id):
        if id in Queue._tasks:
            Queue._tasks.pop(id)
            Queue._idsAvailable.append(id)
            print(" Removed ID {}".format(id))
            return
        if id in Queue._doneTasks:
            Queue._doneTasks.pop(id)
            Queue._idsAvailable.append(id)
            print(" Removed ID {}".format(id))
            return
        print("Task not found in queue")

    def checkForID(self,id):
        return id in Queue._tasks or id in Queue._doneTasks    

    @classmethod
    def generateID(self):
        if Queue._idsAvailable:
            return Queue._idsAvailable.pop()
        
        return str(ObjectId())



#This is the global queue all task will be stored here . Sorry
#if you import this entire module you calling this to yourname space
queue=Queue()
queue.start()

