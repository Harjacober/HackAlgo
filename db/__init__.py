import pymongo
from pymongo import MongoClient


client = MongoClient('localhost', 27017)["contestplatform"]

print(client)