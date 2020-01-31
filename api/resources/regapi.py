
from passlib.hash import pbkdf2_sha256 as sha256
from flask_restful import Resource,reqparse,request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity, get_raw_jwt
    )
from bson.objectid import ObjectId
from db.models import Admin,User,Submission
import re
from flask import current_app
from random import randint
import config
from flask_mail import Message
from flask_cors import  cross_origin



resString=r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
testEmailRe=re.compile(resString)


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
    @cross_origin(supports_credentials=True)
    def get(self):
        id=request.args.get("id")

        data=current_app.unregisteredusers.get(id)

        if not data:
            return response(400,"something went wrong.Have you registered?",[])
        
        for category in [Admin(),User()]: #Admin && User name should be unique
            if category.getBy(email=data["email"]): #check if email already exist
                return response(400,"email taken",[])

            if category.getBy(username=data["username"]): #check if username already exist
                return response(400,"usernname taken",[])

        uid = self.category.addDoc(data) 
        current_app.unregisteredusers.pop(id)
        data.pop("pswd");data["uid"]=str(data["_id"]);data.pop("_id")
        return response(200,"Successfully resgistered",{"uniqueid":str(uid)},access_token=create_access_token(data))
        
    @cross_origin(supports_credentials=True)
    def post(self):
        data=reg_parser.parse_args()
        if not testEmailRe.match(data["email"]):
            return response(200,"Invalid email",[])
        if len(data["pswd"]) <6:
            return response(400,"Password lenght must be greater than six",[])   

        for category in [Admin(),User()]: #Admin && User name should be unique
            if category.getBy(email=data["email"]): #check if email already exist
                return response(400,"email taken",[])

            if category.getBy(username=data["username"]): #check if username already exist
                return response(400,"usernname taken",[])    
        

        data["pswd"]=sha256.hash(data["pswd"]) #replace the old pswd arg with new hash passowrd
    
        generatedid=hex(randint(10**9,10**10))
        
        current_app.unregisteredusers[generatedid]=data

        msg = Message("Welcome to CodeGees",
                  sender=config.MAIL_USERNAME,
                  recipients=[data["email"]]
                  )

        userMsg="""
                <b>Thanks for Registering With Us </b><br>
                <p>Complete your Registration using the Code {} </p> 
                """.format(generatedid)

        msg.html = userMsg

        #current_app.mail.send(msg)

        return response(200,"Success!!! Check you email",[generatedid])
        
class UserRegistration(AdminRegistration):
    category=User()

class AdminLogin(Resource):
    category=Admin()
    @cross_origin(supports_credentials=True)
    def get(self):
        return response(300,"Use a POST REQUEST",[])

    @cross_origin(supports_credentials=True)
    def post(self):
        data=login_parser.parse_args()

        user_data=self.category.getBy(username=data["username"]) #fetch user data from the database with username
        
        if user_data and sha256.verify(data["pswd"],user_data["pswd"]): #if user exist and password match
            user_data.pop("pswd");user_data["uid"]=str(user_data["_id"]);user_data.pop("_id")
            return response(200,"login successfuly",{"uniqueid":user_data["uid"]},access_token=create_access_token(user_data))

        user_data=self.category.getBy(email=data["username"])  #fetch user data from the database with email
        if user_data and sha256.verify(data["pswd"],user_data["pswd"]):
            user_data.pop("pswd");user_data["uid"]=str(user_data["_id"]);user_data.pop("_id")
            return response(200,"login successfuly",{"uniqueid":user_data["uid"]},access_token=create_access_token(user_data))

        return response(400,"check the username and password",[])

class UserLogin(AdminLogin):
   category=User()   





