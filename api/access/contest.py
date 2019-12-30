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
init_contest_parser.add_argument('contesttype', required=True)
init_contest_parser.add_argument('desc', required=False)


update_contest_parser = reqparse.RequestParser()
update_contest_parser.add_argument('title', required=True)  
update_contest_parser.add_argument('desc', required=False)
update_contest_parser.add_argument('duration', required=False)
update_contest_parser.add_argument('startdate', help="start date in milliseconds", required=False)
update_contest_parser.add_argument('enddate', help="end date in milliseconds", required=False) 
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
        # generates the roundnumber by simply incrementing the total number of rounds by one
        roundnum = Contest(ctype).getAll().count() + 1
        input_data['roundnum'] = roundnum
        input_data['authors'] = [input_data['creator']]
        input_data['status'] = 0 # 0 means not approved, 1 means approved, -1 means contest is over
        input_data['duration'] = 0
        input_data['startdate'] = 0
        input_data['enddate'] = 0  
        uid = Contest(ctype).addDoc(input_data)
        # notify authors and invite them to make edits

        return response(200, "Contest Created Successfully", {'contestid':str(uid), 'contesttype':ctype})

class UpdateContest(Resource):
    @jwt_required
    def get(self, ctype):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self, ctype):
        input_data = update_contest_parser.parse_args()

        author_username = input_data['authorusername'] 
        contestid = input_data['contestid']
        data = Contest(ctype).getBy(_id=ObjectId(contestid))
        # check if author is authorized
        if author_username not in data['authors']:
            return response(200, "Unauthorized author", [])
        # confirm that start date is not less than 6hrs in the future

        # remove keys that are not needed
        input_data.pop('authors', None)
        input_data.pop('contestype', None)   
        input_data.pop('authorusername', None)   
        input_data.pop('contestid', None)    

        # update the contest details 
        if Contest(ctype).update(params=input_data, _id=ObjectId(contestid)):
            return response(200, "Update Successful", [])
        return response(200, "contestid does not exist",[])      

class AddProblemForContest(Resource):
    @jwt_required
    def get(self, ctype):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self, ctype):    
        input_data = add_prob_parser.parse_args()

        author_username = input_data['authorusername']
        # check if author is authorized
        if author_username not in data['authors']:
            return response(200, "Unauthorized author", [])
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
    def get(self, ctype):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self, ctype):    
        input_data = add_prob_parser.parse_args()

        author_username = input_data['authorusername']
        # check if author is authorized
        if author_username not in data['authors']:
            return response(200, "Unauthorized author", [])
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
    def get(self, ctype):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self, ctype):
        # Only the contest creator can approve    
        input_data = approval_parser.parse_args()

        creator = input_data['creator'] 
        contestid = input_data['contestid']
        data = Contest(ctype).getBy(_id=ObjectId(contestid))
        if creator != data['creator']:
            return response(200, "Not authorized", [])

        # confirm that start date is not less than 6hrs in the future before approval 
        params = {'status': 1}
        if Contest(ctype).update(params=params, _id=ObjectId(contestid)):
            return response(200, "Success", [])    

class AddNewAuthor(Resource): 
    @jwt_required
    def get(self, ctype):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self, ctype):
        input_data = manage_author_parser.parse_args()

        contestid = input_data['contestid']
        author_username = input_data['authorusername']

        update = {'$addToSet': {'authors': author_username}, "$currentDate": { "lastModified": True }}
        # find a way to notify the admin that he has been made an author and add this contest to his list
        if Contest(ctype).flexibleUpdate(update, _id=ObjectId(contestid)):
            return response(200, "Author Added Successfully", [])

        return response(200, "Check the contestid", [])    


class RemoveAuthor(Resource):   
    @jwt_required
    def get(self, ctype):
        return response(300, "Use a POST request", [])

    @jwt_required
    def post(self, ctype):
        input_data = manage_author_parser.parse_args()
        
        contestid = input_data['contestid']
        author_username = input_data['authorusername']

        update = {'$pull': {'authors': author_username}, "$currentDate": { "lastModified": True }}
        # also remove this contest from the admin's list
        if Contest(ctype).flexibleUpdate(update, _id=ObjectId(contestid)):
            return response(200, "Author removed Successfully", [])

        return response(200, "Check the contestid", [])  

class GetContest(Resource):   
    @jwt_required
    def get(self, ctype, contestid):
        exclude = {'_id':0, 'lastModified':0}
        data = Contest(ctype).getBy(params=exclude, _id=ObjectId(contestid))
        if data:
            return response(200, "Success", data)
        return response(200, "Check the contestid", [])    

    @jwt_required
    def post(self, ctype, contestid): 
        exclude = {'_id':0, 'lastModified':0}
        data = Contest(ctype).getBy(params=exclude, _id=ObjectId(contestid))
        if data:
            return response(200, "Success", data ) 
        return response(200, "Check the contestid", [])             