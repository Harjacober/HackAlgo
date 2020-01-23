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
from api.access.utils import Rating
from flask import current_app

from celery import Celery
import config

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
    from api.access.utils import Rating

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
update_contest_parser.add_argument('authorusername', help="username of the author that wants to update a contest", required=False, store_missing=False)  
update_contest_parser.add_argument('contestid', help="contest id assigned upon contest initialization", required=False, store_missing=False)  


add_prob_parser = reqparse.RequestParser()
add_prob_parser.add_argument('authorusername', help = 'This field cannot be blank.', required = True)
add_prob_parser.add_argument('name', help = 'This field cannot be blank', required = True) 
add_prob_parser.add_argument('testcases', type=FileStorage, location = 'files')
add_prob_parser.add_argument('sizeoftestcases', type=int, help = 'This field cannot be blank', required = True)
add_prob_parser.add_argument('answercases', type=FileStorage, location = 'files')
add_prob_parser.add_argument('samplecases', type=FileStorage, location = 'files')
add_prob_parser.add_argument('sizeofsamplecases', type=int, help = 'This field cannot be blank', required = True)
add_prob_parser.add_argument('sampleanswercases', type=FileStorage, location = 'files')
add_prob_parser.add_argument('problemstatement', help = 'This field cannot be blank', required = True) 
add_prob_parser.add_argument('contestid', help = 'This field cannot be blank', required = True)
add_prob_parser.add_argument('timelimit', type=float, help = 'Time in seconds', required = True)
add_prob_parser.add_argument('memorylimit', type=float, help = 'Memory limit in Megabytes', required = True)
add_prob_parser.add_argument('prblmid', help = 'Time in seconds', required = False, store_missing=False)
add_prob_parser.add_argument('prblmscore', type=int, help = 'Time in seconds', required = True)

approval_parser = reqparse.RequestParser()
approval_parser.add_argument("creator", help="username of the admin that initialized the contest", required=True)
approval_parser.add_argument("contestid", required=True) 

manage_author_parser = reqparse.RequestParser()
manage_author_parser.add_argument("creator", required=True) 
manage_author_parser.add_argument("contestid", required=True) 
manage_author_parser.add_argument("authorusername", required=True)



def response(code,msg,data,access_token=""):
    return {"code":code,"msg":msg,"data":data,"access_token":access_token}

class InitializeContest(Resource):
    """
    This method creates a contest template with the title and auhtor
    which can be updated later by the authors of the coontest.
    """
    @jwt_required
    def get(self):
        return response(300, "Use a POST request", [])

    @jwt_required
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
    def get(self, ctype):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self, ctype):
        input_data = update_contest_parser.parse_args()

        author_username = input_data.get('authorusername') 
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
        input_data.pop('authorusername', None)   
        input_data.pop('contestid', None)    

        # update the contest details 
        if Contest(ctype).update(params=input_data, _id=ObjectId(contestid)):
            return response(200, "Update Successful", [])
        return response(400, "contestid does not exist",[])      

class AddProblemForContest(Resource):
    @jwt_required
    def get(self, ctype):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self, ctype):    
        input_data = add_prob_parser.parse_args()

        contestid = input_data.get('contestid')
        author_username = input_data['authorusername']
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
        testcases = input_data.get('testcases').read().decode("utf-8")  
        answercases = input_data.get('answercases').read().decode("utf-8")  
        samplecases = input_data.get('samplecases').read().decode("utf-8")  
        sampleanswercases = input_data.get('sampleanswercases').read().decode("utf-8")  

        input_data['testcases'] = testcases 
        input_data['answercases'] = answercases 
        input_data['samplecases'] = samplecases 
        input_data['sampleanswercases'] = sampleanswercases 

        input_data=dict(input_data)   
        # remove args that are not needed
        input_data.pop('prblmid', None) 

        uid = ContestProblem(ctype, contestid).addDoc(input_data)

        return response(200, "Problem Added", {'contestid':contestid, 'prblmid': str(uid)})

class UpdateProblemForContest(Resource):
    @jwt_required
    def get(self, ctype):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self, ctype):    
        input_data = add_prob_parser.parse_args()

        if 'prblmid' not in input_data:
            return response(400, "prblmid is required", [])
        contestid = input_data.get('contestid')
        author_username = input_data['authorusername']
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
        testcases = input_data.get('testcases').read().decode("utf-8")  
        answercases = input_data.get('answercases').read().decode("utf-8")  
        samplecases = input_data.get('samplecases').read().decode("utf-8")  
        sampleanswercases = input_data.get('sampleanswercases').read().decode("utf-8")  

        input_data['testcases'] = testcases 
        input_data['answercases'] = answercases 
        input_data['samplecases'] = samplecases 
        input_data['sampleanswercases'] = sampleanswercases 

        input_data=dict(input_data) 
        contestid = input_data.get('contestid')
        prblmid = input_data.get('prblmid')
        # remove args that are not needed
        input_data.pop('prblmid', None) 

        if ContestProblem(ctype, contestid).update(input_data, _id=ObjectId(prblmid)):
            return response(200, "Update Successful", [])
        return response(400, "problem id does not exist",[])      


class ApproveContest(Resource):
    @jwt_required
    def get(self, ctype):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self, ctype):
        # Only the contest creator can approve    
        input_data = approval_parser.parse_args()

        creator = input_data['creator'] 
        contestid = input_data['contestid']
        data = Contest(ctype).getBy(_id=ObjectId(contestid))
        if creator != data.get('creator'):
            return response(404, "Not authorized", [])
        # confirm that start date is not less than 12hrs in the future before approval 
        mintime = 12
        starttime = data.get('starttime')
        duration = data.get('duration')
        currentime = datetime.now().timestamp()
        sixhrs = mintime*60*60*1000.0
        task_start_time = starttime + duration/1000 # start the task when the contest is over 
        if starttime < currentime + sixhrs:
            return response(400, "start time must be at least {}hrs in the future".format(mintime), [])

        task_start_time=10*60
        if config.CELERY_TEST:
            #to test the rank function we set this to 1
            task_start_time=2*60
        params = {'status': 00}
        if Contest(ctype).update(params=params, _id=ObjectId(contestid)):
            # schedule task here
            updateRank.apply_async(countdown=task_start_time,args=[contestid, ctype])
            return response(200, "Success", [])  

        return response(400, "check the contestid",[])    

class AddNewAuthor(Resource): 
    @jwt_required
    def get(self, ctype):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self, ctype):
        input_data = manage_author_parser.parse_args()

        contestid = input_data['contestid']
        author_username = input_data['authorusername']
        creator = input_data['creator']  

        data = Contest(ctype).getBy(_id=ObjectId(contestid))
        if creator != data.get('creator'):
            return response(404, "Not authorized", [])

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
    def get(self, ctype):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self, ctype):
        input_data = manage_author_parser.parse_args()
        
        contestid = input_data['contestid']
        author_username = input_data['authorusername']
        creator = input_data['creator']  
        
        data = Contest(ctype).getBy(_id=ObjectId(contestid))
        if creator != data.get('creator'):
            return response(404, "Not authorized", [])

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
    def get(self, ctype, contestid):  
        exclude = {'_id':0, 'lastModified':0}
        data = Contest(ctype).getBy(params=exclude, _id=ObjectId(contestid))
        if data: 
            exclude = {'lastModified':0}
            problems = list(ContestProblem(ctype, contestid).getAll(params=exclude))  
            for problem in problems:
                problem['_id'] = str(problem['_id'])
            data['problems'] = problems
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
    def get(self, ctype, status):
        status_code = {'started':1, 'inreview':0, 'completed':-1, 'active':00}
        if ctype == "all":
            #TODO(jacob) handle this
            pass
        exclude = {'_id':0, 'lastModified':0}
        data = Contest(ctype).getAll(params=exclude, status=status_code[status])
        if data:
            return response(200, "Success", list(data))
        return response(400, "Check the contestid", [])    

    @jwt_required
    def post(self, ctype, status):  
        return response(300, "Not allowed, Use a GET Request", [])   
