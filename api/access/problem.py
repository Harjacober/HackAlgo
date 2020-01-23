from flask_restful import Resource,reqparse
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from flask import jsonify
from werkzeug.datastructures import FileStorage
from db.models import Problem, Admin

add_prob_parser = reqparse.RequestParser()

add_prob_parser.add_argument('author', help = 'username of the admin adding the problem', required=True)
add_prob_parser.add_argument('name', help = 'This field cannot be blank') 
add_prob_parser.add_argument('testcases', type=FileStorage, location = 'files')
add_prob_parser.add_argument('sizeoftestcases', type=int, help = 'This field cannot be blank')
add_prob_parser.add_argument('answercases', type=FileStorage, location = 'files')
add_prob_parser.add_argument('samplecases', type=FileStorage, location = 'files')
add_prob_parser.add_argument('sizeofsamplecases', type=int, help = 'This field cannot be blank')
add_prob_parser.add_argument('sampleanswercases', type=FileStorage, location = 'files')
add_prob_parser.add_argument('problemstatement', help = 'This field cannot be blank')
add_prob_parser.add_argument('category', help = 'This field cannot be blank')
add_prob_parser.add_argument('timelimit', type=float, help = 'Time in seconds')
add_prob_parser.add_argument('memorylimit', type=float, help = 'Memory limit in Megabytes') 
add_prob_parser.add_argument('tags', help = 'Enter tags separated by comma') #TODO complete implementation

req_show_problem_details=reqparse.RequestParser()
req_show_problem_details.add_argument('prblmid', help = 'This field cannot be blank', required = True) 

req_show_problem = reqparse.RequestParser()
req_show_problem.add_argument('category', required=False)
req_show_problem.add_argument('author', required=False)
req_show_problem.add_argument('name', required=False)
req_show_problem.add_argument('start', type=int, required=False)
req_show_problem.add_argument('size', type=int, required=False)

def response(code,msg,data):
    return {"code":code,"msg":msg,"data":data}

class ProblemDetails(Resource):
    """
    Returns full desciption of a problem excluding answercases and sampleanswercase
    """
    @jwt_required
    def get(self):
        input_data=req_show_problem_details.parse_args()

        exclude = {'answercases':0, 'sampleanswercases':0}
        pb=Problem().getBy(params=exclude, _id=ObjectId(input_data["prblmid"]))
        if not pb:
            return response(400, "Problem id does not exist", [])
        pb["_id"]=str(pb["_id"])

        return response(200, "Success", pb)  

    @jwt_required
    def post(self):
        input_data=req_show_problem_details.parse_args()
 
        exclude = {'answercases':0, 'sampleanswercases':0}
        pb=Problem().getBy(params=exclude, _id=ObjectId(input_data["prblmid"]))
        if not pb:
            return response(400, "Problem id does not exist", [])
        pb["_id"]=str(pb["_id"])

        return response(200, "Success", pb)  

class ProblemSet(Resource):
    """
    Returns all problem that match specific search parameters
    """
    @jwt_required
    def get(self, category):
        input_data = req_show_problem.parse_args()

        exclude = {'_id':0, 'testcases':0, 'sizeoftestcases':0, 'answercases':0, 'samplecases':0,
         'sizeofsamplecases':0, 'sampleanswercases':0, 'problemstatement':0}

        if category == "all":
            data = Problem().getAll(params=exclude,start=input_data['start'],size=input_data['size'])
        else:
            data = Problem().getAll(params=exclude,start=input_data['start'],size=input_data['size'], category=category)
            
        data = list(data)
        return response(200, "Success", data)

    @jwt_required    
    def post(self, category):
        input_data = req_show_problem.parse_args()

        exclude = {'_id':0, 'testcases':0, 'sizeoftestcases':0, 'answercases':0, 'samplecases':0,
         'sizeofsamplecases':0, 'sampleanswercases':0, 'problemstatement':0}

        if category == "all":
            data = Problem().getAll(params=exclude,start=input_data['start'],size=input_data['size'])
        else:
            data = Problem().getAll(params=exclude,start=input_data['start'],size=input_data['size'], category=category)
            
        data = list(data)
        return response(200, "Success", data)

class ProblemSearch(Resource):
    """
    Returns all problem that match specific search parameters
    """
    @jwt_required
    def get(self):
        input_data = req_show_problem.parse_args()

        exclude = {'_id':0, 'testcases':0, 'sizeoftestcases':0, 'answercases':0, 'samplecases':0,
         'sizeofsamplecases':0, 'sampleanswercases':0, 'problemstatement':0}

        data = Problem().getAll(params=exclude,start=input_data['start'],size=input_data['size'],
        category=input_data['category'], author=input_data['author'], name=input_data['name'])
        data = list(data)
        return response(200, "Success", data)

    @jwt_required    
    def post(self):
        input_data = req_show_problem.parse_args()

        exclude = {'_id':0, 'testcases':0, 'sizeoftestcases':0, 'answercases':0, 'samplecases':0,
         'sizeofsamplecases':0, 'sampleanswercases':0, 'problemstatement':0}

        data = Problem().getAll(params=exclude,start=input_data['start'],size=input_data['size'],
        category=input_data['category'], author=input_data['author'], name=input_data['name']) 
        data = list(data) 
        return response(200, "Success", data)
 
class ProblemAdd(Resource):
    @jwt_required
    def get(self):
        return response(300, "Use A POST Request", [])  

    @jwt_required
    def post(self):
        input_data = add_prob_parser.parse_args()

        author = input_data.get('author')
        if not Admin().getBy(username=author):
            return response(400, "author is not an admin, check the username", [])
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
        tags = input_data.get('tags').split(',') # create an array of tags 
        input_data['tags'] = tags

        uid = str(Problem().addDoc(input_data))  
        input_data['prblmid'] = uid

        # update the problems tags list
        update = {'$addToSet': {'problemtags': {'$each': tags}}, "$currentDate": { "lastModified": True }}
        problem().flexibleUpdate(update, upsert=True, _id="tags")
        # add reference to the problems field in the admin collection
        update = {'$addToSet': {'problems': uid}, "$currentDate": { "lastModified": True }}
        if Admin().flexibleUpdate(update, username=input_data['author']):
            return response(200, "New Problem Added", {"prblmid":uid})  

        return response(400, "Problem not Added", [])      

class ProblemUpdate(Resource):
    @jwt_required
    def get(self):
        return response(300, "Use A POST Request", [])  

    @jwt_required
    def post(self):
        input_data = add_prob_parser.parse_args()

        author = input_data.get('author')
        if not Admin().getBy(username=author):
            return response(400, "author is not an admin, check the username", [])
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
            tags = input_data.get('tags').split(',') # create an array of tags 
            input_data['tags'] = tags 

        if Problem().update(params=input_data, _id=ObjectId(input_data.get('prblmid'))):
            # update the problems tags list
            update = {'$addToSet': {'problemtags': {'$each': tags}}, "$currentDate": { "lastModified": True }}
            problem().flexibleUpdate(update, upsert=True, _id="tags")
            return response(200, "update successful",[],access_token=create_access_token(data['uniqueid']))

        return response(400, "Problem not updated", [])              

class GetAllProblemTags(Resource):
    @jwt_required
    def get(self, problemid): 

        data = Problem().getBy(_id="tags").get("problemtags")
        return response(200, "Success", data)
        
    @jwt_required    
    def post(self, problemid):
        return response(300, "Method not allowed", [])