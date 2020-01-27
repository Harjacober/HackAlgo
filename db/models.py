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

class Internships(base):
    def __init__(self):
        super().__init__(self)
        self.collection = client["internships"] 

if __name__ == "__main__":
    pass 