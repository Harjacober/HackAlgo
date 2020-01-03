
from flask_restful import Resource,reqparse
from db.models import User,UserRegisteredContest,User,Contest,ContestProblem,Problem,Submission
from flask_jwt_extended import jwt_required
from datetime import datetime
from bson.objectid import ObjectId
from coderunner.problem import ProblemInstance
from werkzeug.datastructures import FileStorage
 
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


run_code_parser = reqparse.RequestParser()
run_code_parser.add_argument('prblmid', help = 'This field cannot be blank. It also accept email', required = True)
run_code_parser.add_argument('userid', help = 'This field cannot be blank', required = True)
run_code_parser.add_argument('ctype', help = 'This field cannot be blank', required = True)
run_code_parser.add_argument('contestid', help = 'This field cannot be blank', required = True)
run_code_parser.add_argument('codecontent', help = 'This field cannot be blank', required = True)
run_code_parser.add_argument('codefile', type=FileStorage, location='files', required = False, store_missing=False)
run_code_parser.add_argument('lang', help = 'This field cannot be blank', required = True)
run_code_parser.add_argument('stype', help = 'This field cannot be blank', required = True)
run_code_parser.add_argument('contestid', help = 'contest id .if submission is made for a contest')



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
        req_data["totalscore"]=0
        req_data["penalty"]=0
        req_data["problemscore"]={}
        req_data["rank"]=1
     
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

            submissions=list(Submission(req_data["userid"]).
                                getAll(params=exclude,prblmid=req_data["prblmid"]))

            return response(200,"Submisions ",submissions)


        return response(400,"request arameters not valid",{})

     




def gradeSubmission(data):
    """
    This method is called in :class: `Task' in task.py to make necessary 
    updates to the database when submission code to a problem in the contest has be run
    """
    userid = data.get('userid')
    contestid = data.get('contestid')
    prblmid = data.get('prblmid')
    verdict = data.get('verdict')
    contest_problem = ContestProblem(ctype, contestid).getBy(_id=ObjectId(prblmid))

    if verdict != "Passed": 
        score = 0 
        penalty = -10
    else:
        score = contest_problem.get('prblmscore')
        penalty = 0

    # update the user score for that problem if the new score is greater than the prev one
    update = {"$set": {'problemscore.{}'.format(prblmid): {'$gte': score}, {'penalty': {'$inc': penalty}}}  
    UserRegisteredContest(userid).flexibleUpdate(update, contestid=contestid)  
    # Update the total score
    reg_contest = UserRegisteredContest(userid).getBy(contestid=contestid)
    problemscore = reg_contest.get('problemscore')
    total_pen = reg_contest.get('penalty')
    totalscore = total_pen
    for each in problemscore:
        totalscore += problemscore[each]
    # update the total score
    update = {"$set": 'totalscore': totalscore}
    UserRegisteredContest(userid).flexibleUpdate(update, contestid=contestid)      
    
    



