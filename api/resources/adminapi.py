
from api.resources.usersapi import UserProfile,UserUpdateProfile
from db.models import Admin
from flask_restful import Resource,reqparse
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId

get_all_added_prob_parser = reqparse.RequestParser()
get_all_added_prob_parser.add_argument('uniqueid', help="Admin unique Id", required=True)

get_all_involved_contest_parser = reqparse.RequestParser()
get_all_involved_contest_parser.add_argument('uniqueid', help="Admin unique Id", required=True)
get_all_involved_contest_parser.add_argument('contesttype', help="contest type", required=True)




def response(code,msg,data):
    return {"code":code,"msg":msg,"data":data}


class AdminUpdateProfile(UserUpdateProfile):
    category = Admin()            

class AdminProfile(UserProfile):
    category = Admin()  

class GetAllAddedProblems(Resource):
    @jwt_required
    def get(self):
        data = get_all_added_prob_parser.parse_args()  
        uid = ObjectId(data['uniqueid'])  
        allProblemsId = Admin().getBy(_id=uid).get('problems')
        # query all problem information using the IDs before sending to the frontend
        exclude = {'_id':0, 'testcases':0, 'sizeoftestcases':0, 'answercases':0, 'samplecases':0,
         'sizeofsamplecases':0, 'sampleanswercases':0, 'problemstatement':0}
        problemList = [] 
        for problemId in allProblemsId:  
            problemList.append(Problem().getBy(params=exclude, _id=ObjectId(problemId)))

        return response(200, "Success", problemList)    

        
    @jwt_required    
    def post(self):
        return response(300, "Use a POST Request", "")     

class GetAllInvolvedContest(Resource):
    @jwt_required
    def get(self):
        data = get_all_involved_contest_parser.parse_args()  
        uid = ObjectId(data['uniqueid'])  
        ctype = data.get('contesttype')
        allcontestsId = Admin().getBy(_id=uid).get('contest')
        # query all contests information using the IDs before sending to the frontend
        include = {'_id':1, 'title':1, 'creator':1, 'contesttype':1, 'status':1}
        problemList = [] 
        for contestid in allcontestsId:  
            problemList.append(Contest(ctype).getBy(params=include, _id=ObjectId(contestid)))

        return response(200, "Success", problemList)    

        
    @jwt_required    
    def post(self):
        return response(300, "Use a POST Request", "")    