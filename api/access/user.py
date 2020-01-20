
from flask_restful import Resource,reqparse
from db.models import User,UserRegisteredContest,User,Contest,ContestProblem,Problem,Submission
from flask_jwt_extended import jwt_required
from datetime import datetime
from bson.objectid import ObjectId
from coderunner.problem import ProblemInstance
from werkzeug.datastructures import FileStorage

from coderunner.taskqueue import queue 
from coderunner.task import Task

 
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
run_code_parser.add_argument('codecontent', help = 'This field cannot be blank', required = True)
run_code_parser.add_argument('codefile', type=FileStorage, location='files', required = False, store_missing=False)
run_code_parser.add_argument('lang', help = 'This field cannot be blank', required = True)
run_code_parser.add_argument('stype', help = 'This field cannot be blank', required = True)
run_code_parser.add_argument('contestid', help = 'contest id .if submission is made for a contest')
run_code_parser.add_argument('ctype', help = 'contest type .if submission is made for a contest')



run_code_status_parser = reqparse.RequestParser()
run_code_status_parser.add_argument('taskid', help = 'This field cannot be blank.', required = True)
run_code_status_parser.add_argument('lang', help = 'This field cannot be blank.', required = True)
run_code_status_parser.add_argument('prblmid', help = 'This field cannot be blank', required = True)
run_code_status_parser.add_argument('userid', help = 'This field cannot be blank', required = True)
run_code_status_parser.add_argument('contestid', help = 'contest id .if submission is made for a contest')
run_code_status_parser.add_argument('contesttype', help = 'contest type .if submission is made for a contest')

def response(code,msg,data,access_token=""):
    return {"code":code,"msg":msg,"data":data,"access_token":access_token}

class UserEnterContest(Resource):
    """
    When user choose to enter a contest, the contest is added to contestreg collection 
    where other previous contest info has been added, identified uniquely by the userid.
    It also updates this actual contest document to reflect this participant
    """
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
        req_data["rank"]=2 
 
        problems = list(ContestProblem(req_data['contesttype'], req_data['contestid']).getAll())  # get all problems
        for each in problems:
            req_data["problemscore"][str(each['_id'])] = 0

        #TODO(ab|jacob) move all this to a caching db. REDIS?
        contestid = req_data.get('contestid')
        ctype = req_data.get('contesttype')
        userid = req_data.get("userid")
        contest = Contest(ctype).getBy(
                _id=ObjectId(contestid))
        if not contest:
            return response(400,"Contest not found",{})
        else:
            if contest['status'] == -1:
                return response(400,"Contest has ended",{})
            elif contest['status'] == 0:
                return response(400,"Contest is not active yet",{})

        user = User().getBy(_id=ObjectId(userid))
        if not user:
            return response(400,"User Id not found",{})

        UserRegisteredContest(userid).addDoc(req_data)

        # Update the contest collection with this new participant info 
        default_rating = 1500
        default_volatility = 125
        rating = user.get('contest.rating', default_rating)
        volatility = user.get('contest.volatility', default_volatility)
        timesplayed = user.get('contest.timesplayed', 0)
        userdata = {'uid':userid, 'rating':rating, 'volatility':volatility, 
        'timesplayed':timesplayed, 'currrank': 2, 'currscore': 0}

        update = {"$set": {'participants.{}'.format(userid): userdata}}
        if Contest(ctype).flexibleUpdate(update, _id=ObjectId(contestid)):
            return response(200,"Contest participation history updated",{})

        return response(400,"Unable to enter contest",[])    

class UserContestHistory(Resource):
    @jwt_required
    def get(self):
        return response(300,"Use a Post Request",[])

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

     
class RunContestCode(Resource):
    """
    prepares submitted code and passes it to the :class: `Task` to run submission. 
    Handles adding of the partial submission info to the database.
    """
    @jwt_required
    def get(self):
        return  {"code":300,"msg":"Use A Post Request","data":[]}

    @jwt_required
    def post(self):
        input_data = run_code_parser.parse_args()

        problem_id=input_data["prblmid"] # get id
        contestid = input_data.get('contestid')
        ctype = input_data['ctype']

        # check if contest is still active. either check the contest status or 
        # compare the starttime and duration with the currenttime
        contest = Contest(ctype).getBy(_id=ObjectId(contestid))
        duration = contest.get('duration', 2*60*60*1000.0)
        starttime = contest.get('starttime', datetime.now().timestamp())
        currenttime = datetime.now().timestamp()
        if currenttime > starttime+duration:
            return response(400, "Contest is over", [])

        problem = ContestProblem(ctype, contestid).getBy(_id=ObjectId(problem_id))# fetch the actual problem from database with the problemId 
        if not problem:
            return {"code":400,"msg":"Invalid Problem Id","data":[]}
 
        task_id=queue.generateID()
        codecontent = input_data.get('codecontent')
        userid = input_data.get('userid')
        stype = input_data.get('stype')
        lang = input_data.get('lang')
        codefile = input_data.get('codefile')
        
        task=Task(lang,codecontent,userid,ProblemInstance(problem),task_id,stype,codefile,contestid,ctype)
        queue.add(task_id,task) 

        return {"code":"200","msg":"Task started ","data":[task.toJson()]}


class ContestRunCodeStatus(Resource):
    @jwt_required
    def post(self):
        input_data = run_code_status_parser.parse_args()

        problem_id=input_data["prblmid"]
        contestid = input_data['contestid']
        ctype = input_data['contesttype'] 
        problem = ContestProblem(ctype, contestid).getBy(_id=ObjectId(problem_id))
        if not problem:
            return {"code":404,"msg":"Invalid Problem Id","data":[]}

        user_id=input_data["userid"]
        task_id=input_data["taskid"]
        language=input_data["lang"]

        task=queue.getById(task_id)
 
        if task is None:
            return {"code":"404","msg":"Task not found","data":[]}

        return {"code":"200","msg":"Task state is {} ".format(task.status()),"data":[task.toJson()]}

    @jwt_required
    def get(self):
        return  {"code":"300","msg":"Use A Post Request","data":[]}

    