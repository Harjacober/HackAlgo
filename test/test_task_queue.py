import unittest
from threading import Timer
from time import sleep
from coderunner import task,taskqueue

ids=[]

class testTask(task.Task):
    def __init__(self,id):
        self.id=id

    def run(self,ClientConnection):
        sleep(1)
        ids.append(self.id)
        ClientConnection.send(["DONE",self.id])

class QueueTest(unittest.TestCase):
        def test_queue(self):
            q=taskqueue.Queue()    
            def addToQueue(id):
                q.add(id,testTask(id))
            countoftasks=0
            for i in range(1,10):
                Timer(0,addToQueue,(i,)).start()
                countoftasks+=1
            for i in range(10,20):
                countoftasks+=1
                Timer(0,addToQueue,(i,)).start()
            
            sleep(20)
            self.assertTrue(len(ids)==countoftasks)
            
if __name__ == "__main__":
    unittest.main()