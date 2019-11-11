"""
create needed databases,collection,documents if they don't already exist.
Should be run once before app is started 


"""

from __init__ import client

contestdb = client["contestplatform"]

contestdb["admin"]
contestdb["user"]
contestdb["problem"]
contestdb["comment"]
#more collections to be added  below as it suit the app 



