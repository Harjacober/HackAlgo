"""
Entry Point to the entire application. it is recommeded to keep this file as simple as possible.

"""


from flask import Flask,request
from flask_restful import Api
from flask_jwt_extended import JWTManager

from api.access.user import UserAPI
from api.resources.regapi import AdminRegistration,UserRegistration,AdminLogin,UserLogin
from api.resources.usersapi import UserProfile,UserUpdateProfile,SubmissionInfo,SubmissionList
from api.resources.adminapi import AdminProfile, AdminUpdateProfile
from api.resources.coding import RunCode,RunCodeStatus
from api.access.problem import ProblemAdd,ProblemDetails,ProblemSet,ProblemSearch
from api.access.contest import (InitializeContest,UpdateContest,AddProblemForContest
,UpdateProblemForContest,ApproveContest,AddNewAuthor,RemoveAuthor,GetContest)


app=Flask(__name__)
app.config.from_object('config')

api=Api(app)
jwt = JWTManager(app)


@app.route("/")
def index():
    #server some home page here
    return "Hello who is there!!"

api.add_resource(AdminRegistration, '/admin/registration/')
api.add_resource(UserRegistration, '/user/registration/')
api.add_resource(AdminLogin, '/admin/login/')
api.add_resource(UserLogin, '/user/login/') 

api.add_resource(AdminUpdateProfile, '/admin/profile/update/')
api.add_resource(UserUpdateProfile, '/user/profile/update/')
api.add_resource(AdminProfile, '/admin/profile/')
api.add_resource(UserProfile, '/user/profile/')
api.add_resource(SubmissionInfo, '/user/profile/submissions/')
api.add_resource(SubmissionList, '/user/profile/submissions/<string:problemid>/')
api.add_resource(UserAPI, '/<string:id>')

api.add_resource(RunCode, '/run/code/')
api.add_resource(RunCodeStatus,'/run/code/status/')

api.add_resource(ProblemAdd,'/add/problem/')
api.add_resource(ProblemDetails,'/get/problem/')
api.add_resource(ProblemSearch,'/get/problemset/')
api.add_resource(ProblemSet,'/get/problemset/<string:category>/')

api.add_resource(InitializeContest, '/contest/initialize/')
api.add_resource(UpdateContest, '/contest/<string:ctype>/update/')
api.add_resource(AddNewAuthor, '/contest/<string:ctype>/author/add/')
api.add_resource(RemoveAuthor, '/contest/<string:ctype>/author/remove/')
api.add_resource(AddProblemForContest, '/contest/<string:ctype>/problem/add/')
api.add_resource(UpdateProblemForContest, '/contest/<string:ctype>/problem/update/')
api.add_resource(GetContest, '/contest/<string:ctype>/<string:contestid>/')



if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True,port="9000")
