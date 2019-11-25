
from passlib.hash import pbkdf2_sha256 as sha256
from flask_restful import Resource,reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity, get_raw_jwt
    )

from db.models import Admin,User


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
    category=Admin
    def post(self):
        data=reg_parser.parse_args()
        
        if self.category.getBy(email=data["email"]):
            return response(200,"email taken",[])

        data["pswd"]=sha256.hash(data["pswd"])
        self.category.addDoc(data)

        return response(200,"Successfully resgistered",[],access_token=create_access_token(data["email"]))
    def get(self):
        return response(200,"Method not allowed",[])

class UserRegistration(AdminRegistration):
    category=User

class AdminLogin(Resource):
    category=Admin
    def post(self):
        data=login_parser.parse_args()

        user_data=self.category.getBy(username=data["username"])

        if user_data and sha256.verify(data["pswd"],user_data["pswd"]):
            
            return response(200,"login successfuly",[],access_token=create_access_token(data["username"]+user_data["pswd"]))

        user_data=self.category.getBy(email=data["username"])
        

        if user_data and sha256.verify(data["pswd"],user_data["pswd"]):
            return response(200,"login successfuly",[],access_token=create_access_token(data["username"]+user_data["pswd"]))

        return response(200,"check the username and password",[])

    def get(self):
        return response(200,"Method not allowed",[])

class UserLogin(AdminLogin):
   category=User

