import pymongo
from pymongo import MongoClient
from config import TESTING
from platform import system
 
host="mongo"

if system() =="Windows":
    host="localhost"

if TESTING:
    #making sure the database is empty before performing any operation
    client = MongoClient(host, 27017)
    client.drop_database("contestplatformtesting")
    client=client["contestplatformtesting"]
else:
    client = MongoClient(host, 27017)
    client = client["contestplatform"] 