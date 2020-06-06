import config,secrets,hmac,re,json
from threading import Timer
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
from db import redisClient
from flask import current_app,redirect,render_template
from flask_mail import Message
from flask_cors import  cross_origin
from utils.util import retry,response
import base64



resString=r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
testEmailRe=re.compile(resString)


login_parser = reqparse.RequestParser()
login_parser.add_argument('username', help = 'This field cannot be blank. It also accept email', required = True)
login_parser.add_argument('pswd', help = 'This field cannot be blank', required = True)

reg_parser = reqparse.RequestParser()
reg_parser.add_argument('email', help = 'This field cannot be blank.', required = True)
reg_parser.add_argument('username', help = 'This field cannot be blank.', required = True)
reg_parser.add_argument('pswd', help = 'This field cannot be blank', required = True)

pswd_parser = reqparse.RequestParser()
pswd_parser.add_argument('email', help = 'User regtistered mail',required=True)

valid_pswd_parser = reqparse.RequestParser()
valid_pswd_parser.add_argument('id', help = 'User regtistered mail',required=True)

change_pswd_parser = reqparse.RequestParser()
change_pswd_parser.add_argument('email', help = 'User regtistered mail',required=True)
change_pswd_parser.add_argument("pswd",help="user new password",required=True)
change_pswd_parser.add_argument("changepswdid",help="id sent to email",required=True)

change_authuser_pswd_parser = reqparse.RequestParser()
change_authuser_pswd_parser.add_argument("pswd",help="enter user new password",required=True)

BITS=50

class AdminRegistration(Resource):
    category=Admin()
    @cross_origin(supports_credentials=True)
    def get(self):
        id=request.args.get("id")

        
        if redisClient.hget("unregisteredusers"+self.getType(),id):
            data=json.loads(redisClient.hget("unregisteredusers"+self.getType(),id).decode())
        else:
            return response(400,"something went wrong. Did you supply the corrrect code?",[])
        
        if not data:
            return response(400,"something went wrong. Have you registered?",[])
        
        for category in [Admin(),User()]: #Admin && User name should be unique
            if category.getBy(email=data["email"]): #check if email already exist
                return response(400,"email taken",[])

            if category.getBy(username=data["username"]): #check if username already exist
                return response(400,"usernname taken",[])

        uid = self.category.addDoc(data) 
        redisClient.hdel("unregisteredusers"+self.getType(),id)
        data.pop("pswd");data["uid"]=str(data["_id"]);data.pop("_id")
        return response(200,"Successfully resgistered",{"uniqueid":str(uid)},access_token=create_access_token(data))
        
    @cross_origin(supports_credentials=True)
    def post(self):
        data=reg_parser.parse_args()
        if not testEmailRe.match(data["email"]):
            return response(200,"Invalid email",[])
        if len(data["username"]) <2:
            return response(400,"Username is too short",[]) 
        if len(data["pswd"]) <6:
            return response(400,"Password length must be greater than six",[])   

        for category in [Admin(),User()]: #Admin && User name should be unique
            if category.getBy(email=data["email"]): #check if email already exist
                return response(400,"email taken",[])

            if category.getBy(username=data["username"]): #check if username already exist
                return response(400,"usernname taken",[])    
        

        data["pswd"]=sha256.hash(data["pswd"]) #replace the old pswd arg with new hash passowrd
    
        generatedid=secrets.SystemRandom().getrandbits(BITS)
        redisClient.hset("unregisteredusers"+self.getType(),generatedid,json.dumps(data))

        msg = Message("Welcome to CodeGees",
                  sender=config.MAIL_USERNAME,
                  recipients=[data["email"]]
                  )

        userMsg="""
                <b>Thanks for Registering With Us </b><br>
                <p>Complete your Registration using the Code {} </p> 
                """.format(generatedid)

        msg.html = userMsg
        #start mail send in next .5 sec
        kw={"app-context": current_app._get_current_object()}
        Timer(0,retry,(5,current_app.mail.send,msg),kw).start()
        return response(200,"Success!!! Check you email",[generatedid])
        
    def getType(self):
        return "ADMIN" if isinstance(self.category,Admin) else "USER"
        
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

class ForgetPassword(Resource):
    @cross_origin(supports_credentials=True)
    def  get(self):
        data=pswd_parser.parse_args()
        
        #checking if user is present
        for category in [Admin(),User()]:
            if category.getBy(email=data["email"]):break
        else:
            return response(404,"User Not Found",[])    
        
        msg = Message("Password change request",
                  sender=config.MAIL_USERNAME,
                  recipients=[data["email"]]
                )

        mac=hmac.new(config.SECRET_KEY,digestmod=None)
        emailmac = mac.copy()
        generatedid=hex(secrets.SystemRandom().getrandbits(BITS)).encode("utf-8")
        mac.update(generatedid)
        emailmac.update(str.encode(data["email"]))
        generatedid=base64.b64encode((mac.hexdigest()+":"+emailmac.hexdigest()).encode()).decode()
        
        url="{}/check/password?id={}".format(config.HOST,generatedid)
        redisClient.hset("pendindmacs",generatedid,json.dumps((generatedid,url)))

        userMsg="""
                <b><a href="{}">Click here to change password<a/></b><br>
                
                """.format(url)

        msg.html = userMsg
        kw={"app-context": current_app._get_current_object()}
        Timer(0.1,retry,(5,current_app.mail.send,msg),kw).start()

        return response(200,"Success!!! Check you email",[url])

class ChangePassword(Resource):
    @cross_origin(supports_credentials=True)
    def  post(self):
        data=change_pswd_parser.parse_args()

        for cat in [Admin(),User()]:
            user = cat.getBy(email=data["email"])
            if user:
                category=cat
                break
        else:
            return response(404,"User not found",[])
        
        if len(data["pswd"]) <6:
            return response(400,"Password lenght must be greater than six",[])  

        pending=json.loads(redisClient.hget("pendindmacs",data["changepswdid"]).decode())
        if not pending or len(pending)<2:
            return response(400,"Invalid ID",[])  

        email=base64.b64decode(str.encode(data["changepswdid"])).split(b":")[-1]
        mac=hmac.new(config.SECRET_KEY,digestmod=None)
        mac.update(str.encode(data["email"]))

        if not hmac.compare_digest(email.decode(),mac.hexdigest()):
            return response(400,"Invalid Email",[])  
        
        user["pswd"] =  sha256.hash(data["pswd"])
        uid = ObjectId(user['_id'])
        category.update({"pswd":user["pswd"]}, _id=uid)
        redisClient.hdel("pendindmacs",data["email"])
        return response(200,"Success!!! Password changed",[])


@cross_origin(supports_credentials=True)
def ValidatePassword():
    id=request.args.get("id")
    ok= True if id else False
    pending=json.loads(redisClient.hget("pendindmacs",id).decode())
    ok = ok and pending and len(pending)>1 
    if not ok:
        return render_template("html/404.html")
    return redirect("{}/reset-password/{}/{}".format(config.FRONT_END_HOST,id), code=302)

class ChangeAuthUserPassword(Resource):
    @cross_origin(supports_credentials=True)
    @jwt_required
    def post(self):
        data=change_authuser_pswd_parser.parse_args()
        if len(data["pswd"]) <6:
            return response(400,"Password lenght must be greater than five",[])
        
        identity=get_jwt_identity()
        for cat in [Admin(),User()]:
            user=cat.getBy(username=identity.get("username")) 
            user = user or cat.getBy(email=identity.get("email")) 
            if user:
                category=cat;break
        else:
            return response(404,"User not found",[])

        data["pswd"]=sha256.hash(data["pswd"])

        uid = ObjectId(user['_id'])
        category.update(params=data, _id=uid)
        return response(200,"Success!!! Password changed",[])




        
        


        






