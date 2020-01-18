class base:
    def __init__(self):
        self.collection = None 
        
    def addDoc(self,doc):
        assert self.collection is not None
        return self.collection.insert_one(doc).inserted_id
 
    def getBy(self,params=None,**kwargs):
        return self.collection.find_one(kwargs,params)

    def __init__(self,id):
        self.id=id
         
    def getAll(self, params=None,start=1, size=1000, **kwargs):
        """
        :param start: where query should begin
        :param size: size of data needed
        """
        return self.collection.find(kwargs, params).skip(start-1).limit(size)
 
    def update(self, params,**kwargs):
        return self.collection.update_one(
            kwargs,
            {"$set": params,
            "$currentDate": { "lastModified": True }}
        ).modified_count > 0

    def flexibleUpdate(self, update, **kwargs):
        return self.collection.update_one(
            kwargs,
            update
        ).modified_count > 0     