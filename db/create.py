"""
create needed databases,collection,documents if they don't already exist.
Should be run once before app is started 


"""

from __init__ import client
import os

contestdb = client["contestplatform"]

contestdb["admin"]
contestdb["user"]
contestdb["problem"]
contestdb["comment"]
#more collections to be added  below as it suit the app 


langs=['go', 'py', 'java', 'c', 'c++', 'python', 'python2', 'php', 'js']

for lgn in langs:
    os.mkdir("/tmp/{}".format(lgn))




