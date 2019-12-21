"""
Entry Point to the entire application. it is recommeded to keep this file as simple as possible.

"""


from flask import Flask,request
from flask_restful import Api
from flask_jwt_extended import JWTManager

from api.access.user import UserAPI
from api.resources.regapi import AdminRegistration,UserRegistration,AdminLogin,UserLogin,AdminUpdateProfile,UserUpdateProfile,AdminProfile,UserProfile
from api.resources.coding import RunCode,RunCodeStatus
from api.access.problem import ProblemAdd,ProblemDetails,ProblemsSet


app=Flask(__name__)
app.config.from_object('config')

api=Api(app)
jwt = JWTManager(app)


@app.route("/")
def index():
    #server some home page here
    return "Hello who is there!!"

api.add_resource(AdminRegistration, '/adminreg/')
api.add_resource(UserRegistration, '/userreg/')
api.add_resource(AdminLogin, '/adminlogin/')
api.add_resource(UserLogin, '/userlogin/') 
api.add_resource(AdminUpdateProfile, '/updateadminprofile/')
api.add_resource(UserUpdateProfile, '/updateuserprofile/')
api.add_resource(AdminProfile, '/adminprofile/')
api.add_resource(UserProfile, '/userprofile/')
api.add_resource(UserAPI, '/<string:id>')

api.add_resource(RunCode, '/run/code/')
api.add_resource(RunCodeStatus,'/run/code/status/')
api.add_resource(ProblemAdd,'/add/problem/')
api.add_resource(ProblemDetails,'/get/problem/')
api.add_resource(ProblemsSet,'/get/problems/')


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True,port="9000")
