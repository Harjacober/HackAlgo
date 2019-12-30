import pymongo
from pymongo import MongoClient
from config import TESTING

if TESTING:
    #making sure the database is empty before performing any operation
    client = MongoClient('localhost', 27017)
    client.drop_database("contestplatformtesting")
    client=client["contestplatformtesting"]
else:
    client = MongoClient('localhost', 27017)["contestplatform"]