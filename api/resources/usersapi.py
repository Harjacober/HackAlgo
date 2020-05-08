from flask_restful import Resource,reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity, get_raw_jwt
    )
from bson.objectid import ObjectId
from db.models import User,Submission
from flask_cors import  cross_origin



profile_parser = reqparse.RequestParser() 
profile_parser.add_argument('uniqueid', help='unqueid of user whose profile needs to be updated', required=False, store_missing=False)
profile_parser.add_argument('name', help = '', required = False, store_missing=False)
profile_parser.add_argument('birthday', help = '', required = False, store_missing=False)
profile_parser.add_argument('gender', help = 'should either be male, female or other', required = False, store_missing=False)
profile_parser.add_argument('location', help = '', required = False, store_missing=False)
profile_parser.add_argument('summary', help = 'Brief description about yourself', required = False, store_missing=False)
profile_parser.add_argument('profilephoto', help='Link to profile pictture on storage', required=False, store_missing=False)

getprofile_parser = reqparse.RequestParser()
getprofile_parser.add_argument('uniqueid', help="Accepts username or user unique id", required=False)
getprofile_parser.add_argument('username', help="Accepts username or user unique id", required=False)

getsubmission_parser = reqparse.RequestParser() 
getsubmission_parser.add_argument('submid', required=False) 


def response(code,msg,data,access_token=""):
    return {"code":code,"msg":msg,"data":data,"access_token":access_token}


class UserUpdateProfile(Resource):
    category = User()
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        return response(300, "Use a POST Request", [])  
    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        data = profile_parser.parse_args() 
        #update the profile(document) with unqiueid provided 
        uid = ObjectId(data['uniqueid']) #convert str id to a bson object
        if self.category.update(params=data, _id=uid):
            uid = ObjectId(data['uniqueid'])
            exclude = {'pswd':0, 'lastModified':0}
            user_data = self.category.getBy( params=exclude, _id=uid) 
            user_data['_id'] = str(user_data.get('_id'))
            if user_data:
                return response(200, "update successful",[],access_token=create_access_token(user_data))
            return response(400, "something went wrong",[],access_token="")

        return response(400, "uniqueid does not exist",[])      
 
class UserProfile(Resource):
    category = User()
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        currentUser = get_jwt_identity() #fromk jwt
        userid = currentUser.get("uid")  
        uid = ObjectId(userid)
        exclude = {'pswd':0, 'lastModified':0}
        user_data = self.category.getBy( params=exclude, _id=uid) 
        user_data['_id'] = str(user_data.get('_id'))
        if user_data:
            solvedProblems = dict()
            submissions = Submission(userid).getAll(params={'_id':0}, verdict='Passed')
            for submission in submissions:
                solvedProblems[submission.get('prblmid')] = submission.get('name')
            user_data['solvedProblems'] = solvedProblems
            return response(200, "Success", user_data)

        return response(400, "uniqueid doesn't exist",[])    
    
    @jwt_required
    @cross_origin(supports_credentials=True)
    def put(self):
        data = getprofile_parser.parse_args() 
        uid = ObjectId(data['uniqueid'])
        exclude = {'_id':0, 'pswd':0, 'lastModified':0}
        user_data = self.category.getBy( params=exclude, _id=uid) 
        if user_data:
            return response(200, "Success", user_data)
        return response(400, "uniqueid doesn't exist",[])  

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        return response(300, "Use a GET Request",[])     

class SubmissionInfo(Resource):

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        return response(300, "Use a GET Request", [])  

    @jwt_required
    @cross_origin(supports_credentials=True) 
    def get(self):
        data = getsubmission_parser.parse_args()
        currentUser = get_jwt_identity() #fromk jwt
        userid = currentUser.get("uid") 
        subm_id = data.get('submid')
        exclude = {'_id':0, 'lastModified':0}
        user_submission = Submission(userid).getBy(params=exclude, _id=ObjectId(subm_id))
        if user_submission:
            return response(200, "Success", user_submission)
        return response(400, "Submission doesn't exist", [])    

class SubmissionList(Resource):

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self, problemid): 
        return response(300, "Use a GET Request", [])  
        
    @jwt_required 
    @cross_origin(supports_credentials=True)  
    def get(self, problemid): 
        currentUser = get_jwt_identity() #fromk jwt
        userid = currentUser.get("uid") 
        exclude = {'result':0, 'lastModified':0}
        if problemid == "all":
            submissions = list(Submission(userid).getAll(params=exclude))
        else:   
            submissions = list(Submission(userid).getAll(params=exclude, prblmid=problemid))
        if submissions:    
            for each in submissions:
                each["_id"] = str(each.get("_id"))
            return response(200, "Success", submissions)  
        return response(400, "No matching Submission found", [])



        