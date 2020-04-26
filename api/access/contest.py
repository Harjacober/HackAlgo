from flask_restful import Resource,reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity, get_raw_jwt
    )
from bson.objectid import ObjectId
from db.models import Contest, ContestProblem, Admin, User
from werkzeug.datastructures import FileStorage
from datetime import datetime
from utils.ratingsutil import Rating
from flask import current_app
from flask_cors import  cross_origin
from celery import Celery
import config
import time
from coderunner.problem import ProblemInstance
from utils.contestutil import ContestStatus

current_time_mills = lambda: float(round(time.time() * 1000))

# Initialize Celery
#include should contain app.py module path.
celery = Celery(__name__ ,broker=config.CELERY_BROKER_URL,include=['test.test_app','api.access.contest','app'])
celery.config_from_object(config)

def scoreBoard(participants):
    userScores = ((key, participants[key]['currscore'], participants[key]['timepenalty']) for key in participants)
    sortedScores = sorted(userScores, key=lambda x : (-x[1],x[2])) 
    rank, i = 2, 0
    ans = []
    while i < len(sortedScores):
        ans.append((sortedScores[i][0], rank))
        j = i+1
        count = 1
        while j < len(sortedScores) and sortedScores[i][1] == sortedScores[j][1] and sortedScores[i][2] == sortedScores[j][2]: 
            ans.append((sortedScores[j][0], rank))
            count += 1
            j += 1
        rank += count
        i = j
    return ans

@celery.task
def startContest(contestid, ctype, duration): 
    # This function is going to be run in another process celery's
    # so dont worry much about this imports performances
    from db.models import Contest 
    from bson.objectid import ObjectId 

    # update the status field to indicate that the contest has started
    params = {'status': 1}
    Contest(ctype).update(params=params, _id=ObjectId(contestid))   
    # schedule task to end the contest within the given duration
    duration = (duration/1000) + 10800 # celery takes time in seconds not milliseconds
    updateRank.apply_async(countdown=duration,args=[contestid, ctype])

@celery.task
def updateRank(contestid, ctype):
    if config.CELERY_TEST:
        #JUST write to a file and see if it is updated
        with open("/home/celerytestfile.in","w+") as f:
            f.write("a")
        return
    # This function is going to be run in another process celery's
    # so dont worry much about this imports performances
    from db.models import Contest, ContestProblem, Admin
    from bson.objectid import ObjectId
    from utils import Rating

    # update the status field to indicate that the contest is over
    params = {'status': -1}
    Contest(ctype).update(params=params, _id=ObjectId(contestid)) 
    # compute the rating of the contest participants
    contest = Contest(ctype).getBy(_id=ObjectId(contestid))
    participants = contest.get('participants') # get participants information
    computedRank = scoreBoard(participants) # compute the current rank of each participants
    for uid,rank in computedRank:
        participants[uid]['currrank'] = rank
    updated_participants = Rating(participants).calculateRatings() # let the Rating class handle the rest
    # update each participants rating,volatility & timesplayed in their respective collections
    for userid in updated_participants:
            update = {'$inc': {'contest.timesplayed': 1},
            '$set': {'contest.rating': updated_participants[userid]['new_rating'],
            'contest.volatility': updated_participants[userid]['new_volatility']}}
            User().flexibleUpdate(update, _id=ObjectId(userid))


init_contest_parser = reqparse.RequestParser()
init_contest_parser.add_argument('title', required=True)
init_contest_parser.add_argument('creator', help="the username of the admin that created the contest", required=True) 
init_contest_parser.add_argument('contesttype', required=True)
init_contest_parser.add_argument('desc', required=False)


update_contest_parser = reqparse.RequestParser()
update_contest_parser.add_argument('title', required=True)  
update_contest_parser.add_argument('desc', required=False)
update_contest_parser.add_argument('duration',type=float, help="Duration in milliseconds", required=False)
update_contest_parser.add_argument('starttime',type=float, help="start date in milliseconds", required=False) 
update_contest_parser.add_argument('author', help="username of the author that wants to update a contest", required=False, store_missing=False)  
update_contest_parser.add_argument('contestid', help="contest id assigned upon contest initialization", required=False, store_missing=False)  

 
add_prob_parser = reqparse.RequestParser()
add_prob_parser.add_argument('author', help = 'This field cannot be blank.', required = True)
add_prob_parser.add_argument('name', help = 'This field cannot be blank', store_missing=False) 
add_prob_parser.add_argument('testcases', type=FileStorage, location = 'files', store_missing=False)
add_prob_parser.add_argument('sizeoftestcases', type=int, help = 'This field cannot be blank', store_missing=False)
add_prob_parser.add_argument('answercases', type=FileStorage, location = 'files', store_missing=False)
add_prob_parser.add_argument('samplecases', type=FileStorage, location = 'files', store_missing=False)
add_prob_parser.add_argument('sizeofsamplecases', type=int, store_missing=False)
add_prob_parser.add_argument('sampleanswercases', type=FileStorage, location = 'files', store_missing=False)
add_prob_parser.add_argument('problemstatement', store_missing=False) 
add_prob_parser.add_argument('contestid', store_missing=False)
add_prob_parser.add_argument('timelimit', type=float, store_missing=False)
add_prob_parser.add_argument('memorylimit', type=float, store_missing=False)
add_prob_parser.add_argument('tags', help = 'Enter tags separated by comma', store_missing=False)   
add_prob_parser.add_argument('prblmid', help = 'Time in seconds', required = False, store_missing=False)
add_prob_parser.add_argument('prblmscore', type=int, store_missing=False)

approval_parser = reqparse.RequestParser()
approval_parser.add_argument("creator", help="username of the admin that initialized the contest", required=True)
approval_parser.add_argument("contestid", required=True) 

manage_author_parser = reqparse.RequestParser()
manage_author_parser.add_argument("creator", required=True) 
manage_author_parser.add_argument("contestid", required=True) 
manage_author_parser.add_argument("author", required=True)

get_contests_parser = reqparse.RequestParser()
get_contests_parser.add_argument('page', type=int, help="Page number", required=True)
get_contests_parser.add_argument('limit', type=int, help="size of data", required=True)
get_contests_parser.add_argument('filter')



def response(code,msg,data,access_token=""):
    return {"code":code,"msg":msg,"data":data,"access_token":access_token}

class InitializeContest(Resource):
    """
    This method creates a contest template with the title and auhtor
    which can be updated later by the authors of the coontest.
    """
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        return response(300, "Use a POST Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):

        input_data = init_contest_parser.parse_args()   
        ctype = input_data['contesttype']
        creator = input_data.get('creator')
        #check if creator is registered as an admin
        admin = Admin().getBy(username=creator)
        if not admin:
            return response(400, "Username does not exist", [])
        # generates the roundnumber by simply incrementing the total number of rounds by one
        roundnum = Contest(ctype).getAll().count() + 1
        input_data['roundnum'] = roundnum
        input_data['authors'] = [creator]
        input_data['status'] = 0 # 0 means not approved, 1 means approved, -1 means contest is over
        input_data['duration'] = 0.0
        input_data['starttime'] = 0.0 
        input_data['participants'] = {}  
        uid = Contest(ctype).addDoc(input_data)  

        # add this contest to the creator list
        update = {'$addToSet': {'contests': str(uid)}, "$currentDate": { "lastModified": True }}
        if Admin().flexibleUpdate(update, username=creator):
            return response(200, "Contest Created Successfully", {'contestid':str(uid), 'contesttype':ctype})
        return response(400, "Contest not created", [])

class UpdateContest(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self, ctype):
        return response(300, "Use a POST Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self, ctype):
        input_data = update_contest_parser.parse_args()

        author_username = input_data.get('author') 
        #check if author is registered as an admin
        admin = Admin().getBy(username=author_username)
        if not admin:
            return response(400, "Username does not exist", [])
        contestid = input_data.get('contestid')
        data = Contest(ctype).getBy(_id=ObjectId(contestid))
        if not data:
            return response(400, "check contestid", [])
        # check if author is authorized
        if author_username not in data.get('authors'):
            return response(400, "Unauthorized author", []) 

        # remove keys that are not needed
        input_data.pop('authors', None)
        input_data.pop('contestype', None)   
        input_data.pop('author', None)   
        input_data.pop('contestid', None)    

        # update the contest details 
        if Contest(ctype).update(params=input_data, _id=ObjectId(contestid)):
            return response(200, "Update Successful", [])
        return response(400, "contestid does not exist",[])      

class AddProblemForContest(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self, ctype):
        return response(300, "Use a POST Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self, ctype):    
        input_data = add_prob_parser.parse_args()

        contestid = input_data.get('contestid')
        author_username = input_data['author']
        #check if author is registered as an admin
        admin = Admin().getBy(username=author_username)
        if not admin:
            return response(400, "Username does not exist", [])
        # check if author is authorized
        data = Contest(ctype).getBy(_id=ObjectId(contestid))
        if not data:
            return response(400, "check the contestid", [])
        if author_username not in data.get('authors'):
            return response(400, "Unauthorized author", [])
        # Reads the cases from the uploaded files and decode the byte into a unicode string,
        # before saving it into the database
        if input_data.get('testcases') is not None: 
            testcases = input_data['testcases'].read().decode("utf-8")  
            input_data['testcases'] = testcases 
        if input_data.get('answercases') is not None: 
            answercases = input_data['answercases'].read().decode("utf-8")  
            input_data['answercases'] = answercases 
        if input_data.get('samplecases') is not None: 
            samplecases = input_data['samplecases'].read().decode("utf-8")  
            input_data['samplecases'] = samplecases 
        if input_data.get('sampleanswercases') is not None: 
            sampleanswercases = input_data['sampleanswercases'].read().decode("utf-8")  
            input_data['sampleanswercases'] = sampleanswercases 

        tags = input_data.get('tags')# create an array of tags 
        if tags is not None:
            tags = tags.split(',') 
            input_data['tags'] = tags
            input_data['status'] = 0 
        # remove args that are not needed
        input_data.pop('prblmid', None) 

        uid = ContestProblem(ctype, contestid).addDoc(input_data)

        return response(200, "Problem Added", {'contestid':contestid, 'prblmid': str(uid)})

class UpdateProblemForContest(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self, ctype):
        return response(300, "Use a POST Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self, ctype):    
        input_data = add_prob_parser.parse_args()

        if 'prblmid' not in input_data:
            return response(400, "prblmid is required", [])
        contestid = input_data.get('contestid')
        author_username = input_data['author']
        #check if author is registered as an admin
        admin = Admin().getBy(username=author_username)
        if not admin:
            return response(400, "Username does not exist", [])
        # check if author is authorized
        data = Contest(ctype).getBy(_id=ObjectId(contestid))
        if not data:
            return response(400, "check the contestid", [])
        if author_username not in data.get('authors'):
            return response(400, "Unauthorized author", [])
        # Reads the cases from the uploaded files and decode the byte into a unicode string,
        # before saving it into the database
        if input_data.get('testcases') is not None: 
            testcases = input_data['testcases'].read().decode("utf-8")  
            input_data['testcases'] = testcases 
        if input_data.get('answercases') is not None: 
            answercases = input_data['answercases'].read().decode("utf-8")  
            input_data['answercases'] = answercases 
        if input_data.get('samplecases') is not None: 
            samplecases = input_data['samplecases'].read().decode("utf-8")  
            input_data['samplecases'] = samplecases 
        if input_data.get('sampleanswercases') is not None: 
            sampleanswercases = input_data['sampleanswercases'].read().decode("utf-8")  
            input_data['sampleanswercases'] = sampleanswercases 

        tags = []
        if input_data.get('tags') is not None: 
            tags = input_data.get('tags').split(',') # create an array of tags 1
            input_data['tags'] = tags  
        contestid = input_data.get('contestid')
        prblmid = input_data.get('prblmid')
        # remove args that are not needed
        input_data.pop('prblmid', None) 

        if ContestProblem(ctype, contestid).update(input_data, _id=ObjectId(prblmid)):
            return response(200, "Update Successful", [])
        return response(400, "problem id does not exist",[])      


class ApproveContest(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self, ctype):
        return response(300, "Use a POST Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self, ctype):
        # Only the contest creator can approve    
        input_data = approval_parser.parse_args()

        creator = input_data['creator'] 
        contestid = input_data['contestid']
        contest = Contest(ctype).getBy(_id=ObjectId(contestid))
        if not contest:
            return response(400, "Check the contest id", [])
        if creator != contest.get('creator'):
            return response(400, "Not authorized", [])
        if contest.get('status') == ContestStatus.getStatusCode("active"):
            return response(400, "contest already approved", [])
        # confirm that start date is not less than 12hrs in the future before approval 
        mintime = 12
        starttime = contest.get('starttime')
        duration = contest.get('duration') 
        sixhrs = mintime*60*60*1000.0 
        if starttime < current_time_mills() + sixhrs:
            return response(400, "start time must be at least {}hrs in the future".format(mintime), [])
        
        # query all contest problems
        exclude = {'lastModified':0}
        problems = list(ContestProblem(ctype, contestid).getAll(params=exclude))
        if not problems:
            return response(400, "Contest must have at least one problem", [])
        #confirm that all the contests problem meets specification
        for problem in problems:
            probInstance = ProblemInstance(problem)
            if not probInstance.isValid():
                return response(400, 'Problem "{0}" does not meet specification'.format(probInstance.getName()), [])

        start_contest_time = (starttime - current_time_mills()) / 1000 # celeery takes time in seconds not milliseconds  

        params = {'status': ContestStatus.getStatusCode("active")}
        if Contest(ctype).update(params=params, _id=ObjectId(contestid)):
            # schedule task to start contest here
            startContest.apply_async(countdown=start_contest_time, args=[contestid, ctype, duration])
            
            return response(200, "Success", [])  

        return response(400, "check the contestid",[])    

class ForceStartOrEndContest(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self, ctype, contestid, action):
        return response(300, "Use a POST Request", [])
    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self, ctype, contestid, action): 
        if action == "start":
            params = {'status': 1}
            if Contest(ctype).update(params=params, _id=ObjectId(contestid)):
                return response(200, "Contest forcefully started", [])

            return response(400, "Unable to start contest", [])    
        elif action == "end" :
            params = {'status': -1}
            if Contest(ctype).update(params=params, _id=ObjectId(contestid)):
                # compute the participants rank when contest is forcefully ended
                updateRank.apply_async(countdown=1, args=[contestid, ctype])
                return response(200, "Contest forcefully ended", [])

            return response(400, "Unable to end contest", [])  
        else:
             return response(400, "Invalid action", [])  



class AddNewAuthor(Resource): 
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self, ctype):
        return response(300, "Use a POST Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self, ctype):
        input_data = manage_author_parser.parse_args()

        contestid = input_data['contestid']
        author_username = input_data['author']
        creator = input_data['creator']  

        data = Contest(ctype).getBy(_id=ObjectId(contestid))
        if creator != data.get('creator'):
            return response(400, "Not authorized", [])

        admin = Admin().getBy(username=author_username)
        if not admin:
            return response(400, "Username does not exist", [])
        update = {'$addToSet': {'authors': author_username}, "$currentDate": { "lastModified": True }}
        if Contest(ctype).flexibleUpdate(update, _id=ObjectId(contestid)):
            #TODO find a way to notify the admin that he has been made an author and add this contest to his list
            update = {'$addToSet': {'contests': contestid}, "$currentDate": { "lastModified": True }}
            if Admin().flexibleUpdate(update, username=author_username):
                return response(200, "Author Added Successfully", [])

            return response(400, "Unable to add author", [])       

        return response(400, "Check the contestid", [])    


class RemoveAuthor(Resource):   
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self, ctype):
        return response(300, "Use a POST Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self, ctype):
        input_data = manage_author_parser.parse_args()
        
        contestid = input_data['contestid']
        author_username = input_data['author']
        creator = input_data['creator']  
        
        data = Contest(ctype).getBy(_id=ObjectId(contestid))
        if creator != data.get('creator'):
            return response(400, "Not authorized", [])

        admin = Admin().getBy(username=author_username)
        if not admin:
            return response(400, "Username does not exist", [])    
        update = {'$pull': {'authors': author_username}, "$currentDate": { "lastModified": True }}
        # remove the admin from the author's list
        if Contest(ctype).flexibleUpdate(update, _id=ObjectId(contestid)):
            # also remove this contest from the admin's list
            update = {'$pull': {'contests': contestid}, "$currentDate": { "lastModified": True }}
            if Admin().flexibleUpdate(update, username=author_username):    
                return response(200, "Author removed Successfully", [])

          
        return response(400, "Check the contestid", [])  

class GetContestById(Resource):   
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self, ctype, contestid):  
        currentUser = get_jwt_identity() #fromk jwt
        if not currentUser:
            return response(400, "Invalid token", [])
        userid = currentUser.get("uid")
        exclude = {'_id':0, 'lastModified':0}
        data = Contest(ctype).getBy(params=exclude, _id=ObjectId(contestid))
        if data: 
            if data.get("registeredUsers") is not None: # some people have registered for this particular contest
                if userid in data.get("registeredUsers"): # user has registered for this contest
                    data["registered"] = True
                else:
                    data["registered"] = False
            else:
                # obviously, can't be registered as no one registered
                data["registered"] = False

            #TODO problems should only be shown when user has entered the contest area
            #exclude = {'lastModified':0}
            #problems = list(ContestProblem(ctype, contestid).getAll(params=exclude))  
            #for problem in problems:
            #    problem['_id'] = str(problem['_id'])
            #data['problems'] = problems 
            return response(200, "Success", data)
        return response(400, "Check the contestid", [])    

    @jwt_required
    def post(self, ctype, contestid): 
        exclude = {'_id':0, 'lastModified':0}
        data = Contest(ctype).getBy(params=exclude, _id=ObjectId(contestid))
        if data:
            exclude = {'lastModified':0}
            problems = list(ContestProblem(ctype, contestid).getAll(params=exclude)) 
            problems = list(problems)
            for each in problems:
                each['_id'] = str(each.get('_id'))
            data['problems'] = problems
            data['problems'] = list(problems)
            return response(200, "Success", data)
        return response(400, "Check the contestid", [])   

class GetContest(Resource):   
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self, ctype, status):
        status_code = {'started':1, 'inreview':0, 'completed':-1, 'active':2}
        args = get_contests_parser.parse_args()
        page = args.get('page')
        limit = args.get('limit')
        filters = args.get("filter")
        currentUser = get_jwt_identity() #fromk jwt
        if not currentUser:
            return response(400, "Invalid token", [])
        userid = currentUser.get("uid")
        if status == "all":
            # exclude only inreview contest
            query = dict(status={"$ne": status_code["inreview"]}) 
        else:
            query = dict(status=status_code[status])
        if filters is None: # return all data
            exclude = {'lastModified':0}
            data = list(Contest(ctype).getAll(params=exclude, start=(page-1)*limit, size=limit, **query)) # all contests based on the status specified
            for each in data:
                each["_id"] = str(each.get("_id"))
                if each.get("registeredUsers") is not None: # some people have registered for this particular contest
                    if userid in each.get("registeredUsers"): # user has registered for this contest
                        each["registered"] = True
                    else:
                        each["registered"] = False
                else:
                    # obviously this user can't be registered as nobody has registered yet.
                    each["registered"] = False 

            if data:
                return response(200, "Success", data)
            return response(400, "No contest available yet", [])  
        else:
            if filters=="registered": # return only all contests user has registered for
                exclude = {'lastModified':0}
                query["registeredUsers"] = {"$elemMatch": {"$eq":userid}} 
                data = list(Contest(ctype).getAll(params=exclude, start=(page-1)*limit, size=limit, **query))
                for each in data:
                    each["_id"] = str(each.get("_id"))
                    each["registered"] = True
                if data:
                    return response(200, "Success", data)
                return response(400, "No contest available yet", []) 
            elif filters=="unregistered": # return only all contests user has not registered for
                exclude = {'lastModified':0}
                query["registeredUsers"] = {"$not": {"$elemMatch": {"$eq": userid}}} 
                data = list(Contest(ctype).getAll(params=exclude, start=(page-1)*limit, size=limit, **query))
                for each in data:
                    each["_id"] = str(each.get("_id"))
                if data:
                    return response(200, "Success", data)
                return response(400, "No contest available yet", []) 
            else:
                return response(400, "Invalid filter parameter", [])
        

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self, ctype, status):  
        return response(300, "Use a GET Request", [])  


