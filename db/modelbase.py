class base:
    collection=None
    @classmethod
    def addDoc(self,doc):
        assert self.collection is not None
        id=self.collection.insert_one(doc).inserted_id
        return id

    @classmethod
    def getBy(self,params=None,**kwargs):
        return self.collection.find_one(kwargs,params)

    def __init__(self,id):
        self.id=id
        
    @classmethod
    def getAll(self, params=None,start=0, size=1, **kwargs):
        return self.collection.find(kwargs, params).skip(start).limit(size)

    @classmethod
    def update(self, params,**kwargs):
        return self.collection.update_one(
            kwargs,
            {"$set": params,
            "$currentDate": { "lastModified": True }}
        ).modified_count > 0
       