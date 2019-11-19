from flask_restful import Resource
from db.models import Problem

class ProblemAPI(Resource):
    def get(self,id):
        #TODO authentication here
        return str(User.getBy(bro="code"))
    def post(self,payload):
        pass
        