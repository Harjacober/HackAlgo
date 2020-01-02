from db.models import User
from flask_restful import Resource,reqparse
from db.models import User,UserRegisteredContest,User,Contest,ContestProblem,Problem,Submission
from flask_jwt_extended import jwt_required
from datetime import datetime
from bson.objectid import ObjectId
 
enter_contest_parser = reqparse.RequestParser()
enter_contest_parser.add_argument('userid', required=True)
enter_contest_parser.add_argument('contesttype', help="The type of the contest and contest id are required fields",required=True)
enter_contest_parser.add_argument('contestid', help="the contestid", required=True)

user_contest_history_parser = reqparse.RequestParser()
user_contest_history_parser.add_argument('userid', required=True)

user_submission_history_parser = reqparse.RequestParser()
user_submission_history_parser.add_argument('userid', required=True)
user_submission_history_parser.add_argument('contestid', help="if contestid is valid return all submission categorised by contest")
user_submission_history_parser.add_argument('contesttype', help="required if problem is from a contest")
user_submission_history_parser.\
            add_argument('prblmid', help="if prblmid is valid return all submission categorised by problem",required=True)



def response(code,msg,data,access_token=""):
    return {"code":code,"msg":msg,"data":data,"access_token":access_token}

class UserEnterContest(Resource):
    @jwt_required
    def get(self,id):
        return response("300","Use a Post Request",[])

    @jwt_required
    def post(self):
        req_data=enter_contest_parser.parse_args()
        req_data["timeentered"]=str(datetime.now())
     
        #TODO(ab|jacob) move all this to a caching db. REDIS?
        contest = Contest(req_data["contesttype"]).getBy(
                _id=ObjectId(req_data["contestid"]))
        if not contest:
            return response(400,"Contest not found",{})
        else:
            if contest['status'] == -1:
                return response(400,"Contest has ended",{})
            elif contest['status'] == 0:
                return response(400,"Contest is not active yet",{})

        if not User().getBy(
                _id=ObjectId(req_data["userid"])
            ):
            return response(400,"User Id not found",{})

        UserRegisteredContest(req_data["userid"]).addDoc(req_data)
        return response(200,"Contest participation history updated",{})

class UserContestHistory(Resource):
    @jwt_required
    def get(self):
        return response("300","Use a Post Request",[])

    @jwt_required
    def post(self):
        req_data=user_contest_history_parser.parse_args()
        exclude = {'_id':0, 'lastModified':0}
        #TODO(ab|jacob) move all this to a caching db. REDIS?
        if not User().getBy(
                _id=ObjectId(req_data["userid"])
            ):
            return response(400,"User Id not found",{})

        exclude = {'_id':0, 'lastModified':0}
        return response(
            200,
            "User Contests",
            list(UserRegisteredContest
            (req_data["userid"]).getAll(params=exclude))
        )


class UserSubmissionHistory(Resource):
    @jwt_required
    def get(self,id):
        return response("300","Use a Post Request",[])

    @jwt_required
    def post(self):
        req_data=user_submission_history_parser.parse_args()
        exclude = {'_id':0, 'lastModified':0}

        #TODO(ab|jacob) move all this to a caching db. REDIS?

        if req_data["contesttype"] and req_data["contestid"]:

            if not ContestProblem(req_data["contesttype"],req_data["contestid"]).getBy(
                _id=ObjectId(req_data["prblmid"])
            ):
                return response(400,"Contest not found a",{})

            submissions= list(Submission(req_data["userid"]).\
                                getAll(params=exclude,contestid=req_data["contestid"]))

            return response(200,"Submisions ",submissions)

        if req_data["prblmid"] and Problem().getBy(
                _id=ObjectId(req_data["prblmid"])
            ):

            submissions=[subs for subs in Submission(req_data["userid"]).
                                getAll(params=exclude,prblmid=req_data["prblmid"])]

            return response(200,"Submisions ",submissions)


        return response(400,"request arameters not valid",{})
     
        

