from flask_restful import Resource,reqparse
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from flask import jsonify
from werkzeug.datastructures import FileStorage
from db.models import Problem

add_prob_parser = reqparse.RequestParser()

add_prob_parser.add_argument('author', help = 'This field cannot be blank. It also accept email', required = True)
add_prob_parser.add_argument('name', help = 'This field cannot be blank', required = True) 
add_prob_parser.add_argument('testcases', type=FileStorage, location = 'files')
add_prob_parser.add_argument('sizeoftestcases', help = 'This field cannot be blank', required = True)
add_prob_parser.add_argument('answercases', type=FileStorage, location = 'files')
add_prob_parser.add_argument('samplecases', type=FileStorage, location = 'files')
add_prob_parser.add_argument('sizeofsamplecases', help = 'This field cannot be blank', required = True)
add_prob_parser.add_argument('sampleanswercases', type=FileStorage, location = 'files')
add_prob_parser.add_argument('problemstatement', help = 'This field cannot be blank', required = True)
add_prob_parser.add_argument('category', help = 'This field cannot be blank', required = True)


req_show_problem_details=reqparse.RequestParser()
req_show_problem_details.add_argument('prblid', help = 'This field cannot be blank', required = True) 

req_show_problem = reqparse.RequestParser()
req_show_problem.add_argument('category', required=False)
req_show_problem.add_argument('author', required=False)
req_show_problem.add_argument('name', required=False)
req_show_problem.add_argument('start',type=int, required=False)
req_show_problem.add_argument('size', type=int, required=False)

def response(code,msg,data):
    return {"code":code,"msg":msg,"data":data}

class ProblemDetails(Resource):
    """
    Returns full desciption of a problem excluding answercases and sampleanswercase
    """
    @jwt_required
    def get(self):
        input_data=req_show_problem_details.parse_args()

        exclude = {'answercases':0, 'sampleanswercases':0}
        pb=Problem.getBy(params=exclude, _id=ObjectId(input_data["prblid"]))
        pb["_id"]=str(pb["_id"])

        return response(200, "Success", pb)  

    @jwt_required
    def post(self):
        input_data=req_show_problem_details.parse_args()
 
        exclude = {'answercases':0, 'sampleanswercases':0}
        pb=Problem.getBy(params=exclude, _id=ObjectId(input_data["prblid"]))
        if not pb:
            return response(200, "Problem id does not exist", [])
        pb["_id"]=str(pb["_id"])

        return response(200, "Success", pb)  

class ProblemSet(Resource):
    """
    Returns all problem that match specific search parameters
    """
    @jwt_required
    def get(self, category):
        input_data = req_show_problem.parse_args()
        if category = "all":
            category = {}

        exclude = {'_id':0,'testcases':0, 'sizeoftestcases':0, 'answercases':0, 'samplecases':0,
         'sizeofsamplecases':0, 'sampleanswercases':0, 'problemstatement':0}

        data = Problem.getAll(params=exclude,start=input_data['start'],size=input_data['size'],category=category)
        data = list(data)
        return response(200, "Success", data)

    @jwt_required    
    def post(self, category):
        input_data = req_show_problem.parse_args()
        if category = "all":
            category = {}

        exclude = {'_id':0, 'testcases':0, 'sizeoftestcases':0, 'answercases':0, 'samplecases':0,
         'sizeofsamplecases':0, 'sampleanswercases':0, 'problemstatement':0}

        data = Problem.getAll(params=exclude,start=input_data['start'],size=input_data['size'],category=category) 
        data = list(data) 
        return response(200, "Success", data)

class ProblemSearch(Resource):
    """
    Returns all problem that match specific search parameters
    """
    @jwt_required
    def get(self):
        input_data = req_show_problem.parse_args()

        exclude = {'_id':0,'testcases':0, 'sizeoftestcases':0, 'answercases':0, 'samplecases':0,
         'sizeofsamplecases':0, 'sampleanswercases':0, 'problemstatement':0}

        data = Problem.getAll(params=exclude,start=input_data['start'],size=input_data['size'],
        category=input_data['category'], author=input_data['author'], name=input_data['name'])
        data = list(data)
        return response(200, "Success", data)

    @jwt_required    
    def post(self):
        input_data = req_show_problem.parse_args()

        exclude = {'_id':0, 'testcases':0, 'sizeoftestcases':0, 'answercases':0, 'samplecases':0,
         'sizeofsamplecases':0, 'sampleanswercases':0, 'problemstatement':0}

        data = Problem.getAll(params=exclude,start=input_data['start'],size=input_data['size'],
        category=input_data['category'], author=input_data['author'], name=input_data['name']) 
        data = list(data) 
        return response(200, "Success", data)
 
class ProblemAdd(Resource):
    @jwt_required
    def get(self):

        return response(300, "Use A POST Rewuest", [])  

    @jwt_required
    def post(self):
        """
        Reads the cases from the uploaded .txt file and decode the byte into a unicode string,
        before saving it into the database
        """

        input_data = add_prob_parser.parse_args()
        testcases = input_data['testcases'].read().decode("utf-8")  
        answercases = input_data['answercases'].read().decode("utf-8")  
        samplecases = input_data['samplecases'].read().decode("utf-8")  
        sampleanswercases = input_data['sampleanswercases'].read().decode("utf-8")  
        input_data['testcases'] = testcases 
        input_data['answercases'] = answercases 
        input_data['samplecases'] = samplecases 
        input_data['sampleanswercases'] = sampleanswercases 

        input_data=dict(input_data)

        if not input_data["sizeoftestcases"].isdigit():
            return {"code":"400","msg":"tcases must be a digit str","data":[]}

        if not input_data["sizeofsamplecases"].isdigit():
            return {"code":"400","msg":"ncases must be a digit str","data":[]}

        id = str(Problem.addDoc(input_data))  

        return response(200, "New Problem Added", {"prblid":id})  


        