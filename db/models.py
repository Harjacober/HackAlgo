from db.__init__ import client
from db.modelbase import base

class Admin(base):
    collection=client["admin"]
class User(base):
    collection=client["problem"]
class Problem(base):
    collection=client["user"]

if __name__ == "__main__":
    a=Admin.addDoc({"bro":"code"})
    b=User.addDoc({"bro":"code"})
    c=Problem.addDoc({"bro":"code"})