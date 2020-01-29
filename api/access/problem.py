from flask_restful import Resource,reqparse
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from flask import jsonify
from werkzeug.datastructures import FileStorage
from db.models import Problem, Admin
from flask_cors import  cross_origin

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
add_prob_parser.add_argument('score', type=float, help = 'score denotes the difficulty of the problem') 
add_prob_parser.add_argument('tags', help = 'Enter tags separated by comma') #TODO complete implementation
add_prob_parser.add_argument('prblmid', help = 'for updating problem', store_missing=False) 

submit_prob_parser = reqparse.RequestParser()
submit_prob_parser.add_argument('author', help = 'username of the admin adding the problem', required=True)
submit_prob_parser.add_argument('prblmid', help = 'cannot be empty', required=True)

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
    Returns full description of a problem excluding answercases and sampleanswercase
    """
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        input_data=req_show_problem_details.parse_args()

        exclude = {'answercases':0, 'sampleanswercases':0, 'lastModified':0}
        pb=Problem().getBy(params=exclude, _id=ObjectId(input_data["prblmid"]))
        if not pb:
            return response(400, "Problem id does not exist", [])
        pb["_id"]=str(pb["_id"])

        return response(200, "Success", pb)  

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self): 
        return response(300, "Method not Allowed", [])  

class ProblemSet(Resource):
    """
    Returns all problem that match specific search parameters
    """
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self, category):
        input_data = req_show_problem.parse_args()

        exclude = {'_id':0, 'testcases':0, 'sizeoftestcases':0, 'answercases':0, 'samplecases':0,
         'sizeofsamplecases':0, 'sampleanswercases':0, 'problemstatement':0, 'lastModified':0}

        if category == "all":
            data = Problem().getAll(params=exclude,start=input_data['start'],size=input_data['size'], status=1)
        else:
            data = Problem().getAll(params=exclude,start=input_data['start'],size=input_data['size'], 
            category=category, status=1)
            
        data = list(data)
        return response(200, "Success", data)

    @jwt_required
    @cross_origin(supports_credentials=True)  
    def post(self, category):
        input_data = req_show_problem.parse_args()

        exclude = {'_id':0, 'testcases':0, 'sizeoftestcases':0, 'answercases':0, 'samplecases':0,
         'sizeofsamplecases':0, 'sampleanswercases':0, 'problemstatement':0, 'lastModified':0} 

        if category == "all":
            data = Problem().getAll(params=exclude,start=input_data['start'],size=input_data['size'],status=1)
        else:
            data = Problem().getAll(params=exclude,start=input_data['start'],size=input_data['size'], 
            category=category, status=1)
            
        data = list(data)
        return response(200, "Success", data)

class ProblemSearch(Resource):
    """
    Returns all problem that match specific search parameters
    """
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        input_data = req_show_problem.parse_args()

        exclude = {'_id':0, 'testcases':0, 'sizeoftestcases':0, 'answercases':0, 'samplecases':0,
         'sizeofsamplecases':0, 'sampleanswercases':0, 'problemstatement':0, 'lastModified':0}

        data = Problem().getAll(params=exclude,start=input_data['start'],size=input_data['size'],
        category=input_data['category'], author=input_data['author'], name=input_data['name'], status=1)
        data = list(data)
        return response(200, "Success", data)

    @jwt_required 
    @cross_origin(supports_credentials=True)  
    def post(self):
        input_data = req_show_problem.parse_args()

        exclude = {'_id':0, 'testcases':0, 'sizeoftestcases':0, 'answercases':0, 'samplecases':0,
         'sizeofsamplecases':0, 'sampleanswercases':0, 'problemstatement':0, 'lastModified':0} 

        data = Problem().getAll(params=exclude,start=input_data['start'],size=input_data['size'],
        category=input_data['category'], author=input_data['author'], name=input_data['name'], status=1) 
        data = list(data) 
        return response(200, "Success", data)
 
class ProblemAdd(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        return response(300, "Use A POST Request", [])  

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        input_data = add_prob_parser.parse_args()
        difficulty = {"800-1100":"easy", "1200-1500":"medium", "1600-2000":"hard", "2100-2500":"advanced"} #TODO make this global

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
        input_data['status'] = 0
        # process difficulty
        score = input_data.get('score')
        for key in difficulty:
            lower,upper = list(map(int, key.split("-")))
            if int(score) >= lower and score <= upper:
                input_data['difficulty'] = difficulty[key]
                break

        uid = str(Problem().addDoc(input_data))  
        input_data['prblmid'] = uid

        # update the problems tags list
        update = {"$set":{'_id':"tags"},'$addToSet': {'problemtags': {'$each': tags}}, "$currentDate": { "lastModified": True }}
        Problem().flexibleUpdate(update, upsert=True, _id="tags")
        # add reference to the problems field in the admin collection
        update = {'$addToSet': {'problems': uid}, "$currentDate": { "lastModified": True }}
        if Admin().flexibleUpdate(update, username=input_data['author']):
            return response(200, "New Problem Added", {"prblmid":uid})  

        return response(400, "Problem not Added", [])      

class ProblemUpdate(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        return response(300, "Use A POST Request", [])  

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        input_data = add_prob_parser.parse_args()
        difficulty = {"800-1100":"easy", "1200-1500":"medium", "1600-2000":"hard", "2100-2500":"advanced"} #TODO make this global
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
            tags = input_data.get('tags').split(',') # create an array of tags 1
            input_data['tags'] = tags 
        # process difficulty
        score = input_data.get('score')
        if score is not None:
            for key in difficulty:
                lower,upper = list(map(int, key.split("-")))
                if int(score) >= lower and score <= upper:
                    input_data['difficulty'] = difficulty[key]
                    break
                
        # status = 0 to ensure problem can't be edited after submission, but.. does that make sense? I'm not sure.
        # perhaps changes should be allowed when the problem has been submitted.
        if Problem().update(params=input_data, _id=ObjectId(input_data.get('prblmid')), status=0):
            # update the problems tags list
            update = {'$addToSet': {'problemtags': {'$each': tags}}, "$currentDate": { "lastModified": True }}
            Problem().flexibleUpdate(update, upsert=True, _id="tags")
            return response(200, "update successful",[])

        return response(400, "Problem not updated", [])              

class GetAllProblemTags(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self): 

        data = Problem().getBy(_id="tags").get("problemtags")
        return response(200, "Success", data)
        
    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self, problemid):
        return response(300, "Method not allowed", [])

class SubmitProblem(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        return response(300, "Use A POST Request", [])  

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        input_data = submit_prob_parser.parse_args()

        author = input_data.get('author')
        pb = Problem().getBy(_id=ObjectId(input_data["prblmid"]))
        if not pb:
            return response(400, "Problem not found", [])
        if author != pb.get('author'): 
            return response(400, "not the author of the problem", [])  
         
        params = {"status": 1}
        if Problem().update(params=params, _id=ObjectId(input_data['prblmid'])):
            return response(200, "Problem submitted", [])     

        return response(400, "Problem not submitted", [])     