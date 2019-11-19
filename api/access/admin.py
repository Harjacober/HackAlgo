from flask_restful import Resource
from db.models import Admin

class AdminAPI(Resource):
    def get(self,id):
        #TODO authentication here
        return str(Admin.getBy(bro="code"))
    def post(self,payload):
        pass
        