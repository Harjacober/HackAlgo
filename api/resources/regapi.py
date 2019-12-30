
from passlib.hash import pbkdf2_sha256 as sha256
from flask_restful import Resource,reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity, get_raw_jwt
    )
from bson.objectid import ObjectId
from db.models import Admin,User,Submission


login_parser = reqparse.RequestParser()
login_parser.add_argument('username', help = 'This field cannot be blank. It also accept email', required = True)
login_parser.add_argument('pswd', help = 'This field cannot be blank', required = True)

reg_parser = reqparse.RequestParser()
reg_parser.add_argument('email', help = 'This field cannot be blank.', required = True)
reg_parser.add_argument('username', help = 'This field cannot be blank.', required = True)
reg_parser.add_argument('pswd', help = 'This field cannot be blank', required = True)

profile_parser = reqparse.RequestParser() 
profile_parser.add_argument('uniqueid', help='unqueid of user whose profile needs to be updated', required=False, store_missing=False)
profile_parser.add_argument('name', help = '', required = False, store_missing=False)
profile_parser.add_argument('birthday', help = '', required = False, store_missing=False)
profile_parser.add_argument('gender', help = 'should either be male, female or other', required = False, store_missing=False)
profile_parser.add_argument('location', help = '', required = False, store_missing=False)
profile_parser.add_argument('summary', help = 'Brief description about yourself', required = False, store_missing=False)
profile_parser.add_argument('profilephoto', help='Link to profile pictture on storage', required=False, store_missing=False)

getprofile_parser = reqparse.RequestParser()
getprofile_parser.add_argument('uniqueid', help="This field cannot be blank", required=True)

getsubmission_parser = reqparse.RequestParser()
getsubmission_parser.add_argument('userid', required=True)
getsubmission_parser.add_argument('prblid', required=False)
getsubmission_parser.add_argument('submid', required=False )

def response(code,msg,data,access_token=""):
    return {"code":code,"msg":msg,"data":data,"access_token":access_token}

class AdminRegistration(Resource):
    category=Admin()
    def get(self):
        return response(300,"Method not allowed",[]) 
        
    def post(self):
        data=reg_parser.parse_args()
        
        if self.category.getBy(email=data["email"]): #check if email already exist
            return response(200,"email taken",[])
        if self.category.getBy(username=data["username"]): #check if username already exist
            return response(200,"usernname taken",[])    

        data["pswd"]=sha256.hash(data["pswd"]) #replace the old pswd arg with new hash passowrd
        uid = self.category.addDoc(data) #finally add registration data to database

        return response(200,"Successfully resgistered",{"uniqueid":str(uid)},access_token=create_access_token(data["email"]))

class UserRegistration(AdminRegistration):
    category=User()

class AdminLogin(Resource):
    category=Admin()
    def get(self) -> dict:
        return response(300,"Method not allowed",[])

    def post(self) -> dict:
        data=login_parser.parse_args()

        user_data=self.category.getBy(username=data["username"]) #fetch user data from the database with username
        if user_data and sha256.verify(data["pswd"],user_data["pswd"]): #if user exist and password match
            return response(200,"login successfuly",{"uniqueid":str(user_data.get('_id'))},access_token=create_access_token(data["username"]+user_data["pswd"]))

        user_data=self.category.getBy(email=data["username"])  #fetch user data from the database with email
        if user_data and sha256.verify(data["pswd"],user_data["pswd"]):
            return response(200,"login successfuly",{"uniqueid":str(user_data.get('_id'))},access_token=create_access_token(data["username"]+user_data["pswd"]))

        return response(200,"check the username and password",[])

class UserLogin(AdminLogin):
   category=User() 

class UserUpdateProfile(Resource):
    category = User()
    def get(self):
        return response(300, "Method not allowed", [])  

    def post(self):
        data = profile_parser.parse_args() 
        #update the profile(document) with unqiueid provided 
        uid = ObjectId(data['uniqueid']) #convert str id to a bson object
        if self.category.update(params=data, _id=uid):
            return response(200, "update successful",[],access_token=create_access_token(data['uniqueid']))

        return response(200, "uniqueid does not exist",[])      

class AdminUpdateProfile(UserUpdateProfile):
    category = Admin()        

class UserProfile(Resource):
    category = User()
    def get(self):
        data = getprofile_parser.parse_args() 
        uid = ObjectId(data['uniqueid'])
        exclude = {'_id':0, 'pswd':0, 'lastModified':0}
        user_data = self.category.getBy( params=exclude, _id=uid) 
        if user_data:
            return response(200, "Success", user_data)
        return response(200, "uniqueid doesn't exist",[])    

    def post(self):
        data = getprofile_parser.parse_args() 
        uid = ObjectId(data['uniqueid'])
        exclude = {'_id':0, 'pswd':0, 'lastModified':0}
        user_data = self.category.getBy( params=exclude, _id=uid) 
        if user_data:
            return response(200, "Success", user_data)
        return response(200, "uniqueid doesn't exist",[])        

class AdminProfile(UserProfile):
    category = Admin()

class SubmissionInfo(Resource):

    @jwt_required
    def get(self):
        return response(300, "Method not allowed", [])

    @jwt_required    
    def post(self):
        data = getsubmission_parser.parse_args()
        userid = data['userid']
        subm_id = data['submid']
        exclude = {'_id':0, 'lastModified':0}
        user_submission = Submission(userid).getBy(params=exclude, _id=ObjectId(subm_id))
        if user_submission:
            return response(200, "Success", user_submission)
        return response(200, "Submission doesn't exist", [])    

class SubmissionList(Resource):

    @jwt_required
    def get(self, problemid): 
        return response(300, "Method not allowed", [])
        
    @jwt_required    
    def post(self, problemid):
        data = getsubmission_parser.parse_args()
        userid = data['userid'] 
        exclude = {'_id':0, 'codecontent': 0, 'result':0, 'lastModified':0}
        if problemid == "all":
            submissions = Submission(userid).getAll(params=exclude)
        else:   
            submissions = Submission(userid).getAll(params=exclude, prblmid=problemid)
        if submissions:    
            return response(200, "Success", list(submissions))   
        return response(200, "No matching Submission found", [])            





