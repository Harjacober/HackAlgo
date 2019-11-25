from flask_restful import Resource,reqparse
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from flask import jsonify

from db.models import Problem

req_parser = reqparse.RequestParser()

req_parser.add_argument('author', help = 'This field cannot be blank. It also accept email', required = True)
req_parser.add_argument('name', help = 'This field cannot be blank', required = True)
req_parser.add_argument('cases', help = 'This field cannot be blank', required = True)
req_parser.add_argument('ncases', help = 'This field cannot be blank', required = True)
req_parser.add_argument('answercases', help = 'This field cannot be blank', required = True)
req_parser.add_argument('tcases', help = 'This field cannot be blank', required = True)
req_parser.add_argument('ntcases', help = 'This field cannot be blank', required = True)
req_parser.add_argument('problemstatement', help = 'This field cannot be blank', required = True)
req_parser.add_argument('category', help = 'This field cannot be blank', required = True)

req_show_problem=reqparse.RequestParser()
req_show_problem.add_argument('prblid', help = 'This field cannot be blank', required = True)

class ProblemAPI(Resource):
    @jwt_required
    def get(self):
        input_data=req_show_problem.parse_args()

        pb=Problem.getBy(_id=ObjectId(input_data["prblid"]))
        pb["_id"]=str(pb["_id"])

        return  {"code":"200","msg":"","data":[pb]}

    @jwt_required
    def post(self):
        input_data=req_show_problem.parse_args()
 
        pb=Problem.getBy(_id=ObjectId(input_data["prblid"]))
        pb["_id"]=str(pb["_id"])

        return  {"code":"200","msg":"","data":[str(pb)]}
        

class ProblemAdd(Resource):
    @jwt_required
    def get(self):

        return  {"code":"300","msg":"Use A Post Request","data":[]}

    @jwt_required
    def post(self):
        input_data=dict(req_parser.parse_args())

        if not input_data["ncases"].isdigit():
            return {"code":"400","msg":"tcases must be a digit str","data":[]}

        if not input_data["ntcases"].isdigit():
            return {"code":"400","msg":"ncases must be a digit str","data":[]}

        id=str(Problem.addDoc(input_data).id)

        return {"code":"200","msg":"New Problem added","data":[id]}


        