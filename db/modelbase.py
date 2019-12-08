class base:
    collection=None
    @classmethod
    def addDoc(self,doc):
        assert self.collection is not None
        id=self.collection.insert_one(doc).inserted_id
        return id

    @classmethod
    def getBy(self,**kwargs):
        return self.collection.find_one(kwargs)

    def __init__(self,id):
        self.id=id
        

    def get(self):
        return self.collection.find_one({"_id": self.id})

    @classmethod
    def update(self, params,**kwargs):
        return self.collection.update_one(
            kwargs,
            {"$set": params,
            "$currentDate": { "lastModified": True }}
        ).modified_count > 0
       