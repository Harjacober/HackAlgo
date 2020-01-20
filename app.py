"""
Entry Point to the entire application. it is recommeded to keep this file as simple as possible.

"""

from flask import Flask, request
from flask_restful import Api
from flask_jwt_extended import JWTManager

from api.resources.regapi import AdminRegistration, UserRegistration, AdminLogin, UserLogin
from api.resources.usersapi import UserProfile, UserUpdateProfile, SubmissionInfo, SubmissionList
from api.resources.adminapi import AdminProfile, AdminUpdateProfile
from api.resources.coding import RunCode, RunCodeStatus
from api.access.problem import ProblemAdd, ProblemDetails, ProblemSet, ProblemSearch
from api.access.contest import (InitializeContest, UpdateContest,
                                AddProblemForContest, UpdateProblemForContest,
                                ApproveContest, AddNewAuthor, RemoveAuthor,
                                GetContest, GetContestById)
from api.access.user import UserEnterContest, UserContestHistory, UserSubmissionHistory, RunContestCode, ContestRunCodeStatus
from flask_socketio import SocketIO

from celery import Celery
import config



contestplatform = Flask(__name__)
contestplatform.config.from_object('config')


api = Api(contestplatform)
jwt = JWTManager(contestplatform)


contestplatform.socketio = SocketIO(contestplatform)

@contestplatform.route("/")
def index():
    #server some home page here
    return "Welcome to HackAlgo!!"

api.add_resource(AdminRegistration, '/admin/registration/')
api.add_resource(UserRegistration, '/user/registration/')
api.add_resource(AdminLogin, '/admin/login/')
api.add_resource(UserLogin, '/user/login/')

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
api.add_resource(ProblemDetails, '/get/problem/')
api.add_resource(ProblemSearch, '/get/problemset/')
api.add_resource(ProblemSet, '/get/problemset/<string:category>/')

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

api.add_resource(UserEnterContest, '/enter/contest/')
api.add_resource(RunContestCode, '/contest/run/code/')
api.add_resource(ContestRunCodeStatus, '/contest/run/code/status/')
api.add_resource(UserContestHistory, '/my/contest/history/')
api.add_resource(UserSubmissionHistory, '/my/submission/history/')

if __name__ == "__main__":
    contestplatform.socketio.run(contestplatform,host="0.0.0.0", debug=True, port="9000")
