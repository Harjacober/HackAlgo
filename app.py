"""
Entry Point to the entire application. it is recommeded to keep this file as simple as possible.

"""

from flask import Flask, request
from flask_restful import Api
from flask_jwt_extended import JWTManager,jwt_required

from api.resources.regapi import AdminRegistration, UserRegistration, AdminLogin, UserLogin, ForgetPassword, ValidatePassword,ChangePassword,ChangeAuthUserPassword
from api.resources.usersapi import UserProfile, UserUpdateProfile, SubmissionInfo, SubmissionList
from api.resources.adminapi import AdminProfile, AdminUpdateProfile,GetAllAddedProblems, GetAllInvolvedContest
from api.resources.coding import RunCode, RunCodeStatus
from api.access.problem import ProblemAdd, ProblemDetails, ProblemSet, ProblemSearch, ProblemUpdate, SubmitProblem, GetAllProblemTags, DeleteProblem
from api.access.contest import (InitializeContest, UpdateContest,
                                AddProblemForContest, UpdateProblemForContest,
                                ApproveContest, AddNewAuthor, RemoveAuthor,
                                GetContest, GetContestById, ForceStartOrEndContest, DeleteContest)
from api.access.user import UserRegisterForContest, UserEnterContest, UserContestHistory, UserContestSubmissionHistoryById, UserContestSubmissionHistory, RunContestCode, ContestRunCodeStatus
from api.resources.internship import AddInternship,GetInternships,ViewInternship
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_cors import CORS,cross_origin


from celery import Celery
import config


contestplatform = Flask(__name__)
contestplatform.config.from_object('config')


api = Api(contestplatform)
jwt = JWTManager(contestplatform)

mail = Mail()
mail.init_app(contestplatform)
contestplatform.mail=mail

ws=SocketIO(contestplatform,cors_allowed_origins="*")
ws.init_app(contestplatform)
contestplatform.socketio = ws

CORS(contestplatform,support_credentials=True)

@contestplatform.route("/")
def index():
    #serve some home page here
    return "Welcome to HackAlgo!!"

@jwt_required
@cross_origin
@contestplatform.socketio.on('connect')
def on_connect():
    contestplatform.socketio.send("Welcome to HackAlgo!!")


contestplatform.add_url_rule("/check/password/","checkPassword",ValidatePassword)

api.add_resource(AdminRegistration, '/admin/registration/')
api.add_resource(UserRegistration, '/user/registration/')
api.add_resource(AdminLogin, '/admin/login/')
api.add_resource(UserLogin, '/user/login/')
api.add_resource(ForgetPassword,"/forgot/password/")
api.add_resource(ChangePassword,"/change/password/")
api.add_resource(ChangeAuthUserPassword,"/change/password/authuser/")

api.add_resource(GetAllAddedProblems, '/admin/get/addedproblems/all/')
api.add_resource(GetAllInvolvedContest, '/admin/get/involvedcontests/all/')
api.add_resource(AdminUpdateProfile, '/admin/profile/update/')
api.add_resource(UserUpdateProfile, '/user/profile/update/')
api.add_resource(AdminProfile, '/admin/profile/')
api.add_resource(UserProfile, '/user/profile/')
api.add_resource(SubmissionInfo, '/user/profile/submissions/')
api.add_resource(SubmissionList,
                 '/user/profile/submissions/<string:problemid>/')

api.add_resource(RunCode, '/run/code/')
api.add_resource(RunCodeStatus, '/run/code/status/')

api.add_resource(ProblemAdd, '/add/problem/')
api.add_resource(ProblemUpdate, '/update/problem/')
api.add_resource(SubmitProblem, '/submit/problem/')
api.add_resource(ProblemDetails, '/get/problem/')
api.add_resource(GetAllProblemTags, '/get/problemtags/')
api.add_resource(ProblemSearch, '/get/problemset/')
api.add_resource(ProblemSet, '/get/problemset/<string:category>/')
api.add_resource(DeleteProblem, '/delete/problem/')

api.add_resource(InitializeContest, '/contest/initialize/')
api.add_resource(UpdateContest, '/contest/<string:ctype>/update/')
api.add_resource(AddNewAuthor, '/contest/<string:ctype>/author/add/')
api.add_resource(RemoveAuthor, '/contest/<string:ctype>/author/remove/')
api.add_resource(AddProblemForContest, '/contest/<string:ctype>/problem/add/')
api.add_resource(UpdateProblemForContest,
                 '/contest/<string:ctype>/problem/update/')
api.add_resource(ApproveContest, '/contest/<string:ctype>/approve/')
api.add_resource(GetContestById, '/contest/<string:ctype>/<string:contestid>/')
api.add_resource(GetContest, '/contest/many/<string:ctype>/<string:status>/')
api.add_resource(ForceStartOrEndContest, '/contest/force/<string:ctype>/<string:contestid>/<string:action>/')
api.add_resource(DeleteContest, '/contest/<string:ctype>/delete/')

api.add_resource(UserEnterContest, '/enter/contest/')
api.add_resource(UserRegisterForContest, '/register/contest/')
api.add_resource(RunContestCode, '/contest/run/code/')
api.add_resource(ContestRunCodeStatus, '/contest/run/code/status/')
api.add_resource(UserContestHistory, '/my/contest/history/')
api.add_resource(UserContestSubmissionHistory, '/my/submission/history/')
api.add_resource(UserContestSubmissionHistoryById, '/my/submission/history/single/')

api.add_resource(AddInternship, '/add/internship/')
api.add_resource(GetInternships, '/get/internship/')
api.add_resource(ViewInternship, '/view/internship/')
