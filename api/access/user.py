
from flask_restful import Resource,reqparse
from db.models import User,UserRegisteredContest,User,Contest,ContestProblem,Problem,Submission
from flask_jwt_extended import jwt_required,get_jwt_identity
from datetime import datetime
from bson.objectid import ObjectId
from coderunner.problem import ProblemInstance
from werkzeug.datastructures import FileStorage
from flask_cors import  cross_origin

from coderunner.taskqueue import queue 
from coderunner.task import Task
from utils.contestutil import ContestStatus
from utils.util import SupportedLanguages,response

 
enter_contest_parser = reqparse.RequestParser() 
enter_contest_parser.add_argument('contesttype', help="The type of the contest and contest id are required fields",required=True)
enter_contest_parser.add_argument('contestid', help="the contestid", required=True)

register_for_contest_parser = reqparse.RequestParser() 
register_for_contest_parser.add_argument('contesttype', help="The type of the contest and contest id are required fields",required=True)
register_for_contest_parser.add_argument('contestid', help="the contestid", required=True)

user_submission_history_parser = reqparse.RequestParser() 
user_submission_history_parser.add_argument('contestid', help="if contestid is valid return all submission categorised by contest",required=True)
user_submission_history_parser.add_argument('contesttype', help="required if problem is from a contest",required=True)
user_submission_history_parser.\
            add_argument('prblmid', help="if prblmid is valid return all submission categorised by problem")

user_single_submission_parser = reqparse.RequestParser()
user_single_submission_parser.add_argument("submid", help="Submission id", required=True)


run_code_parser = reqparse.RequestParser()
run_code_parser.add_argument('prblmid', help = 'This field cannot be blank. It also accept email', required = True) 
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
run_code_status_parser.add_argument('contestid', help = 'contest id .if submission is made for a contest')
run_code_status_parser.add_argument('contesttype', help = 'contest type .if submission is made for a contest')


class UserEnterContest(Resource):
    """
    When user choose to enter a contest, the contest is added to contestreg collection 
    where other previous contest info has been added, identified uniquely by the userid.
    It also updates this actual contest document to reflect this participant
    """
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self,id):
        return response(300, "Use a POST Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self): 
        req_data=enter_contest_parser.parse_args()

        contestid = req_data.get('contestid')
        ctype = req_data.get('contesttype') 
        req_data["timeentered"]=str(datetime.now())
        req_data["totalscore"]=0
        req_data["penalty"]=0
        req_data["problemscore"]={}
        req_data["rank"]=2  

        currentUser = get_jwt_identity() #fromk jwt
        userid = currentUser.get("uid") 
        req_data["userid"]=userid

        contest = Contest(ctype).getBy(_id=ObjectId(contestid)) 
        if not contest:
            return response(400,"Contest not found",{})
        else:
            if contest['status'] == ContestStatus.getStatusCode("active"):
                return response(400,"Contest is yet to start",{})
            elif contest['status'] == ContestStatus.getStatusCode("completed"):
                return response(400,"Contest has ended",{})
            elif contest['status'] == ContestStatus.getStatusCode("inreview"):
                return response(400,"Contest is not active yet",{})
        req_data["title"]=contest.get("title") #required as part of the information to be stored in `UserRegisteredContest` collection

        user = User().getBy(_id=ObjectId(userid))
        if not user:
            return response(400,"User Id not found",{})

        # query all contest problems
        exclude = {'lastModified':0, 'testcases':0, 'answercases':0,'sizeoftestcases':0}
        problems = list(ContestProblem(ctype, contestid).getAll(params=exclude))  
        for problem in problems:
            problem['_id'] = str(problem['_id'])
            req_data["problemscore"][str(problem['_id'])] = 0 
        contest['problems'] = problems 
        contest['_id'] = str(contest.get('_id'))
        
        if userid in contest.get("participants"): # user already entered before
            return response(200,
            "Contest participation history updated",contest) 

        if contest.get("registeredUsers") is not None: # some people have registered for this particular contest
            if userid not in contest.get("registeredUsers"): # user has not registered for this contest
                return response(400, "User not registered for this contest",{})
        else:
            # obviously, can't be registered as no one registered
            return response(400, "User not registered for this contest",{}) 

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
            return response(200,
            "Contest participation history updated",contest)

        return response(400,"Unable to enter contest",[])    

class UserContestHistory(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        return response(300, "Use a GET Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self): 

        currentUser = get_jwt_identity() #fromk jwt
        userid = currentUser.get("uid") 
        exclude = {'_id':0, 'lastModified':0}
        #TODO(ab|jacob) move all this to a caching db. REDIS?
        if not User().getBy(
                _id=ObjectId(userid)
            ):
            return response(400,"User Id not found",{})

        exclude = {'_id':0, 'lastModified':0}
        data = list(UserRegisteredContest(userid).getAll(params=exclude))
        if data:
            return response(200,"Success",data)
        
        return response(400,"No contest data available",[])


class UserContestSubmissionHistory(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        return response(300, "Use a GET Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        req_data=user_submission_history_parser.parse_args()
        currentUser = get_jwt_identity() #fromk jwt
        userid = currentUser.get("uid") 
        ctype = req_data.get("contesttype")
        contestid = req_data.get("contestid")
        prblmid = req_data.get("prblmid")
        exclude = {'lastModified':0}

        #TODO(ab|jacob) move all this to a caching db. REDIS? 

        user = User().getBy(_id=ObjectId(userid))
        if not user:
            return response(400,"User Id not found",{})

        if not Contest(ctype).getBy(_id=ObjectId(contestid)):
            return response(400, "Contest not found", [])
        # return submissions to all contests problems
        if not prblmid:
            submissions= list(Submission(userid).getAll(params=exclude,contestid=contestid)) 
            for each in submissions:
                each["_id"] = str(each.get("_id"))
            return response(200, "Success", submissions) 
        # if problem id is invalid
        if not ContestProblem(ctype, contestid).getBy(_id=ObjectId(prblmid)):
            return response(400, "check the problem id", [])

        submissions=list(Submission(userid).getAll(params=exclude,prblmid=prblmid))
        for each in submissions:
                each["_id"] = str(each.get("_id"))
        return response(200,"Success",submissions) 

class UserContestSubmissionHistoryById(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        return response(300, "Use a GET Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        req_data=user_single_submission_parser.parse_args()
        currentUser = get_jwt_identity() #fromk jwt
        userid = currentUser.get("uid") 
        submid = req_data.get("submid") 
        exclude = {'_id':0, 'lastModified':0}

        #TODO(ab|jacob) move all this to a caching db. REDIS?  
        user = User().getBy(_id=ObjectId(userid))
        if not user:
            return response(400,"User Id not found",{})

        submissions = Submission(userid).getBy(params=exclude, _id=ObjectId(submid))
        if submissions:
            return response(200,"Success",submissions) 
        else:
            return response(400, "No submission corresponding to that Id", [])

     
class RunContestCode(Resource):
    """
    prepares submitted code and passes it to the :class: `Task` to run submission. 
    Handles adding of the partial submission info to the database.
    """
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        return response(300, "Use a POST Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        input_data = run_code_parser.parse_args()

        problem_id=input_data.get("prblmid") # get id
        contestid = input_data.get('contestid')
        ctype = input_data.get('ctype')
        codecontent = input_data.get('codecontent')
        currentUser = get_jwt_identity() #fromk jwt
        userid = currentUser.get("uid")
        stype = input_data.get('stype')
        lang = input_data.get('lang')
        if lang not in SupportedLanguages:
            return response(400, "Specified language not supported", [])
        codefile = input_data.get('codefile')

        user = User().getBy(_id=ObjectId(userid))
        if not user:
            return response(400,"User Id not found",{})
        # check if contest is still active. either check the contest status or 
        # compare the starttime and duration with the currenttime
        contest = Contest(ctype).getBy(_id=ObjectId(contestid))
        if not contest:
            return response(400, "Check the contest id", [])
        duration = contest.get('duration', 2*60*60*1000.0)
        starttime = contest.get('starttime', datetime.now().timestamp())
        currenttime = datetime.now().timestamp()
        if currenttime > starttime+duration:
            return response(400, "Contest is over", [])

        problem = ContestProblem(ctype, contestid).getBy(_id=ObjectId(problem_id))# fetch the actual problem from database with the problemId 
        if not problem:
            return response(400, "Invalid Problem Id", []) 
 
        task_id=queue.generateID()
        
        task=Task(lang,codecontent,userid,ProblemInstance(problem),task_id,stype,codefile,contestid,ctype)
        queue.add(task_id,task) 

        return response(200,"Task started",[task.toJson()]) 


class ContestRunCodeStatus(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        input_data = run_code_status_parser.parse_args()

        problem_id=input_data.get("prblmid")
        contestid = input_data.get('contestid')
        ctype = input_data.get('contesttype')
        currentUser = get_jwt_identity() #fromk jwt
        userid = currentUser.get("uid") 

        user = User().getBy(_id=ObjectId(userid))
        if not user:
            return response(400,"User Id not found",{})
        problem = ContestProblem(ctype, contestid).getBy(_id=ObjectId(problem_id))
        if not problem:
             return response(400, "Invalid Problem Id", [])  
        task_id=input_data["taskid"]
        language=input_data["lang"]

        task=queue.getById(task_id)
        if task is None:
             return response(400, "Task not found", [])  

        return response(200,"Task state is {} ".format(task.status()),[task.toJson()]) 

    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        return response(300, "Use A POST Request", [])  


class UserRegisterForContest(Resource):
    """
    When user choose to register for a contest, it doesn't guarantee they will paritcipate in the contest.
    """
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self,id):
        return response(300, "Use A POST Request", [])  

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        req_data=register_for_contest_parser.parse_args() 

        #TODO(ab|jacob) move all this to a caching db. REDIS?
        contestid = req_data.get('contestid')
        ctype = req_data.get('contesttype')
        currentUser = get_jwt_identity() #fromk jwt
        if not currentUser:
            return response(400, "User Id not found", [])
        userid = currentUser.get("uid")
        contest = Contest(ctype).getBy( _id=ObjectId(contestid))
        if not contest:
            return response(400,"Contest not found",{})
        else:
            if contest['status'] == ContestStatus.getStatusCode("started"):
                return response(400,"Contest has already started",{})
            elif contest['status'] == ContestStatus.getStatusCode("completed"):
                return response(400,"Contest has ended",{})
            elif contest['status'] == ContestStatus.getStatusCode("inreview"):
                return response(400,"Contest is not active yet",{})
 
        user = User().getBy(_id=ObjectId(userid))
        if not user:
            return response(400,"User Id not found",{})
 
        # Update the contest collection with this new registered participant info   
        update = {"$addToSet": {'registeredUsers': userid}}
        if Contest(ctype).flexibleUpdate(update, upsert=True, _id=ObjectId(contestid)):
            return response(200,"Registration Success",{})

        return response(400,"Unable to register for contest",[])    
