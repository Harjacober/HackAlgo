from flask_restful import Resource,reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity, get_raw_jwt
    )
from bson.objectid import ObjectId
from db.models import Contest, ContestProblem
from werkzeug.datastructures import FileStorage


init_contest_parser = reqparse.RequestParser()
init_contest_parser.add_argument('title', required=True)
init_contest_parser.add_argument('creator', help="the username of the admin that created the contest", required=True)
init_contest_parser.add_argument('authors', help="username of the admin that can make edit to this contest", required=True, action='append')
init_contest_parser.add_argument('contesttype', required=True)
init_contest_parser.add_argument('desc', required=False)
init_contest_parser.add_argument('duration', required=False)
init_contest_parser.add_argument('startdate', help="start date in milliseconds", required=False)
init_contest_parser.add_argument('enddate', help="end date in milliseconds", required=False) 
init_contest_parser.add_argument('author_username', help="username of the author that wants to update a contest", required=False, store_missing=False)  
init_contest_parser.add_argument('contestid', help="contest id assigned upon contest initialization", required=False, store_missing=False)  

add_prob_parser = reqparse.RequestParser()
add_prob_parser.add_argument('author', help = 'This field cannot be blank. It also accept email', required = True)
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
        # generates the roundnumber by simply incrementing the total number of rounds by one
        roundnum = Contest(ctype).getAll().count() + 1
        input_data['roundnum'] = roundnum
        input_data['status'] = 0 # 0 means not approved, 1 means approved, -1 means contest is over
        # remove args that are not needed
        input_data.pop('contestype', None)   
        input_data.pop('author_username', None)   
        input_data.pop('contestid', None)    

        uid = Contest(ctype).addDoc(input_data)
        # notify authors and invite them to make edits

        return response(200, "Contest Created Successfully", {'contestid':str(uid)})

class UpdateContest(Resource):
    @jwt_required
    def get(self):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self):
        input_data = init_contest_parser.parse_args()

        author_username = input_data['author_username']
        # check if author is authorized
        ctype = input_data['contesttype'] 
        contestid = input_data['contestid']
        data = Contest(ctype).getBy(_id=ObjectId(contestid))
        if author_username not in data['authors']:
            return response(200, "Unauthorized author", [])

        # remove keys that are not needed
        input_data.pop('contestype', None)   
        input_data.pop('author_username', None)   
        input_data.pop('contestid', None)    

        # update the contest details 
        if Contest(ctype).update(params=input_data, _id=ObjectId(contestid)):
            return response(200, "Update Successful", [])
        return response(200, "contestid does not exist",[])      

class AddProblemForContest(Resource):
    @jwt_required
    def get(self):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self):    
        input_data = add_prob_parser.parse_args()
        # Reads the cases from the uploaded files and decode the byte into a unicode string,
        # before saving it into the database
        testcases = input_data['testcases'].read().decode("utf-8")  
        answercases = input_data['answercases'].read().decode("utf-8")  
        samplecases = input_data['samplecases'].read().decode("utf-8")  
        sampleanswercases = input_data['sampleanswercases'].read().decode("utf-8")  

        input_data['testcases'] = testcases 
        input_data['answercases'] = answercases 
        input_data['samplecases'] = samplecases 
        input_data['sampleanswercases'] = sampleanswercases 

        input_data=dict(input_data) 
        contestid = input_data['contestid']
        # remove args that are not needed
        input_data.pop('prblmid', None) 

        uid = ContestProblem(ctype, contestid).addDoc(input_data)

        return response(200, "Problem Added", {'contestid':contestid, 'prblmid': uid})

class UpdateProblemForContest(Resource):
    @jwt_required
    def get(self):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self):    
        input_data = add_prob_parser.parse_args()
        # Reads the cases from the uploaded files and decode the byte into a unicode string,
        # before saving it into the database
        testcases = input_data['testcases'].read().decode("utf-8")  
        answercases = input_data['answercases'].read().decode("utf-8")  
        samplecases = input_data['samplecases'].read().decode("utf-8")  
        sampleanswercases = input_data['sampleanswercases'].read().decode("utf-8")  

        input_data['testcases'] = testcases 
        input_data['answercases'] = answercases 
        input_data['samplecases'] = samplecases 
        input_data['sampleanswercases'] = sampleanswercases 

        input_data=dict(input_data) 
        contestid = input_data['contestid']
        prblmid = input_data['prblmid']
        # remove args that are not needed
        input_data.pop('prblmid', None) 

        if ContestProblem(ctype, contestid).update(input_data, _id=prblmid):
            return response(200, "Update Successful", [])
        return response(200, "problem id does not exist",[])      


class ApproveContest(Resource):
    @jwt_required
    def get(self):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self):
        # Only the contest creator can approve    
        input_data = approval_parser.parse_args()

        creator = input_data['creator']
        ctype = input_data['contesttype'] 
        contestid = input_data['contestid']
        data = Contest(ctype).getBy(_id=ObjectId(contestid))
        if creator != data['creator']:
            return response(200, "Not authorized", [])

        params = {'status': 1}
        if Contest(ctype).update(params=params, _id=objectId(contestid)):
            return response(200, "Success", [])    

