from db.__init__ import client
from db.modelbase import base


class Admin(base):
    collection=client["admin"]
class User(base):
    collection=client["user"]
class Problem(base):
    collection=client["problem"]

if __name__ == "__main__":
    pass
    #from bson.objectid import ObjectId
    #a=Admin.getBy(_id= ObjectId("5dd4309c7ea41f4d84bcbf3d"))
    #print(a)
    #a=Admin.addDoc({"bro":"code"})
    #b=User.addDoc({"bro":"code"})
    #c=Problem.addDoc({"bro":"code"})
