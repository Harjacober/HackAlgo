class base:
    collection=None
    @classmethod
    def addDoc(self,doc):
        assert self.collection is not None
        id=self.collection.insert_one(doc).inserted_id
        return base(id)

    @classmethod
    def getBy(self,**kwargs):
        return self.collection.find_one(kwargs)

    def __init__(self,id):
        self.id=id
        

    def get(self):
        return self.collection.find_one({"_id": self.id})


    def update(self,params: dict,**kwargs):
        return self.collection.updateOne(
            kwargs,
            {"$set": params},
            {"$currentDate": { lastModified: true }}
        ).modified_count >0
       