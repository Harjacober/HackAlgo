from db.__init__ import client
from db.modelbase import base


class Admin(base):
    def __init__(self):
        super().__init__(self)
        self.collection = client["admin"]  
        
class User(base):
    def __init__(self):
        super().__init__(self)
        self.collection = client["user"]  
    
class Problem(base):
    def __init__(self):
        super().__init__(self)
        self.collection = client["problem"]

class Submission(base):
    def __init__(self, userid):
        super().__init__(self)
        usercollection = client["user"]
        submissioncollection = usercollection["submission"]
        self.collection = submissioncollection[userid]

class Contest(base):
    def __init__(self, ctype):
        super().__init__(self)
        contest = client['contest']
        types = contest[ctype]     
        self.collection = types 

class UserRegisteredContest(base):
    def __init__(self, userid):
        super().__init__(self)
        self.collection = client['contestreg'][userid]
 
class ContestProblem(Contest):
    def __init__(self, ctype, contestid):
        Contest.__init__(self, ctype)   
        self.collection = self.collection[contestid]      

if __name__ == "__main__":
    pass
    #from bson.objectid import ObjectId
    #a=Admin.getBy(_id= ObjectId("5dd4309c7ea41f4d84bcbf3d"))
    #print(a)
    #a=Admin.addDoc({"bro":"code"})
    #b=User.addDoc({"bro":"code"})
    #c=Problem.addDoc({"bro":"code"})
