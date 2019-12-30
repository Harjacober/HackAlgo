
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





