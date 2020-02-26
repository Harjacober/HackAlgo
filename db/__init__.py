import pymongo
from pymongo import MongoClient
from config import TESTING
from platform import system
import redis
 
if TESTING:
    #making sure the database is empty before performing any operation
    client = MongoClient("mongo", 27017)
    client.drop_database("contestplatformtesting")
    client=client["contestplatformtesting"]
    redisClient = redis.Redis(host='redis', port=6379, db=1)
else:
    client = MongoClient("mongo", 27017)
    client = client["contestplatform"] 
    redisClient = redis.Redis(host='redis', port=6379, db=0)

