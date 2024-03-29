from flask_restful import Resource,reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity 
from bson.objectid import ObjectId
from flask import jsonify
from werkzeug.datastructures import FileStorage
from db.models import Problem, Admin
from flask_cors import  cross_origin
from coderunner.problem import ProblemInstance
from utils.util import response

add_prob_parser = reqparse.RequestParser()

add_prob_parser.add_argument('author', help = 'username of the admin adding the problem', required=True)
add_prob_parser.add_argument('name', store_missing=False) 
add_prob_parser.add_argument('testcases', type=FileStorage, location='files', store_missing=False)
add_prob_parser.add_argument('sizeoftestcases', type=int)
add_prob_parser.add_argument('answercases', type=FileStorage, location = 'files', store_missing=False)
add_prob_parser.add_argument('samplecases', type=FileStorage, location = 'files', store_missing=False)
add_prob_parser.add_argument('sizeofsamplecases', type=int, store_missing=False)
add_prob_parser.add_argument('sampleanswercases', type=FileStorage, location = 'files', store_missing=False)
add_prob_parser.add_argument('problemstatement', store_missing=False)
add_prob_parser.add_argument('category', store_missing=False)
add_prob_parser.add_argument('timelimit', type=float, help = 'Time in seconds', store_missing=False)
add_prob_parser.add_argument('memorylimit', type=float, help = 'Memory limit in Megabytes', store_missing=False) 
add_prob_parser.add_argument('score', type=float, help = 'score denotes the difficulty of the problem', store_missing=False) 
add_prob_parser.add_argument('tags', help = 'Enter tags separated by comma', store_missing=False)   
add_prob_parser.add_argument('prblmid', help = 'for updating problem', store_missing=False) 

add_prob_parser_plain= add_prob_parser.copy()
add_prob_parser_plain.replace_argument("testcases",store_missing=False)
add_prob_parser_plain.replace_argument("answercases",store_missing=False)
add_prob_parser_plain.replace_argument("samplecases",store_missing=False)
add_prob_parser_plain.replace_argument("sampleanswercases",store_missing=False)

submit_prob_parser = reqparse.RequestParser()
submit_prob_parser.add_argument('author', help = 'username of the admin adding the problem', required=True)
submit_prob_parser.add_argument('prblmid', help = 'cannot be empty', required=True)

req_show_problem_details=reqparse.RequestParser()
req_show_problem_details.add_argument('prblmid', help = 'This field cannot be blank', required = True) 

req_show_problem = reqparse.RequestParser()
req_show_problem.add_argument('tags', required=False) 
req_show_problem.add_argument('page', type=int, required=True, help="This field cannot be blank")
req_show_problem.add_argument('limit', type=int, required=True, help="This field cannot be blank")
req_show_problem.add_argument('filter')

delete_problem_parser = reqparse.RequestParser()
delete_problem_parser.add_argument('author', help = 'username of the admin deleting the problem', required=True)
delete_problem_parser.add_argument('prblmid', help = 'cannot be empty', required=True)
 

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
        return response(300, "Use a GET Request", [])

class ProblemSet(Resource):
    """
    Returns all problem that match specific search parameters
    """
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self, category):
        input_data = req_show_problem.parse_args()

        include = {'_id':1,'prblmid':1, 'author':1, 'name':1, 'category':1, 'score':1, 'tags':1, 'difficulty':1, 'solvedby':1}

        currentUser = get_jwt_identity() # get id from token
        if not currentUser:
            return response(400, "Invalid token", [])
        userid = currentUser.get("uid")
        page = input_data.get('page')
        limit = input_data.get('limit')
        if category == "all":
            data = list(Problem().getAll(params=include,start=(page-1)*limit,size=limit, status=1))
        else:
            data = list(Problem().getAll(params=include,start=(page-1)*limit,size=limit, 
            category=category, status=1))
            
        for each in data:
            each["_id"] = str(each.get("_id"))
            if userid in each.get("solvedby"): # check if the user requesting has solved the problem before
                each["solved"] = True
            else:
                each["solved"] = False

        return response(200, "Success", data)

    @jwt_required
    @cross_origin(supports_credentials=True)  
    def post(self, category): 
        return response(300, "Use a GET Request", data)

class ProblemSearch(Resource):
    """
    Returns all problem that match specific search parameters
    """
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        input_data = req_show_problem.parse_args()

        include = {'_id':1,'prblmid':1, 'author':1, 'name':1, 'category':1, 'score':1, 'tags':1, 'difficulty':1, 'solvedby':1}

        currentUser = get_jwt_identity() # get id from token
        if not currentUser:
            return response(400, "Invalid token", [])
        userid = currentUser.get("uid")
        tags = input_data.get('tags')
        page = input_data.get('page')
        limit = input_data.get('limit')
        filters = input_data.get('filter')
        if tags is None:
            query = dict(status=1)
        else:
            value = {'$all': tags.split(",")}
            query = dict(tags=value,status=1)
        if filters is None:
            data = list(Problem().getAll(params=include,start=(page-1)*limit,size=limit,**query))
            for each in data:
                each["_id"] = str(each.get("_id"))
                if userid in each.get("solvedby"): # check if the user requesting has solved the problem before
                    each["solved"] = True
                else:
                    each["solved"] = False
            
            if data:
                return response(200, "Success", list(data))
            else:
                return response(400, "No problem available yet", [])
        else:
            if filters=="solved": # return only all contests user has registered for 
                query["solvedby"] = {"$elemMatch": {"$eq": userid}}
                data = list(Problem().getAll(params=include,start=(page-1)*limit,size=limit,**query))
                for each in data:
                    each["_id"] = str(each.get("_id"))
                if data:
                    return response(200, "Success", data)
                return response(400, "No problem available yet", []) 
            elif filters=="unsolved": # return only all contests user has not registered for 
                query["solvedby"] = {"$not": {"$elemMatch": {"$eq": userid}}}
                data = list(Problem().getAll(params=include,start=(page-1)*limit,size=limit,**query))
                for each in data:
                    each["_id"] = str(each.get("_id"))
                if data:
                    return response(200, "Success", data)
                return response(400, "No problem available yet", []) 
            else:
                return response(400, "Invalid filter parameter", [])

    @jwt_required 
    @cross_origin(supports_credentials=True)  
    def post(self): 
        return response(300, "Use a GET Request", [])
 
class ProblemAdd(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        return response(300, "Use a POST Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        input_data = add_prob_parser.parse_args()
        input_data_plain = add_prob_parser_plain.parse_args()
        difficulty = {"800-1100":"easy", "1200-1500":"medium", "1600-2000":"hard", "2100-2500":"advanced"} #TODO make this global

        author = input_data.get('author')
        if not Admin().getBy(username=author):
            return response(400, "author is not an admin, check the username", [])
        # Reads the cases from the uploaded files and decode the byte into a unicode string,
        # before saving it into the database
        if input_data.get('testcases') is not None: 
            testcases = input_data['testcases'].read().decode("utf-8")  
            input_data['testcases'] = testcases 
        else:
            input_data['testcases']=input_data_plain['testcases']
        if input_data.get('answercases') is not None: 
            answercases = input_data['answercases'].read().decode("utf-8")  
            input_data['answercases'] = answercases 
        else:
            input_data['answercases']=input_data_plain['answercases']
        if input_data.get('samplecases') is not None: 
            samplecases = input_data['samplecases'].read().decode("utf-8")  
            input_data['samplecases'] = samplecases 
        else:
            input_data['samplecases'] = input_data_plain['samplecases'] 
        if input_data.get('sampleanswercases') is not None: 
            sampleanswercases = input_data['sampleanswercases'].read().decode("utf-8")  
            input_data['sampleanswercases'] = sampleanswercases 
        else:
            input_data['sampleanswercases'] = input_data_plain['sampleanswercases']
        tags = input_data.get('tags')# create an array of tags 
        if tags is not None:
            tags = tags.split(',') 
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
        return response(300, "Use a POST Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        input_data = add_prob_parser.parse_args()
        input_data_plain = add_prob_parser_plain.parse_args()
        difficulty = {"800-1100":"easy", "1200-1500":"medium", "1600-2000":"hard", "2100-2500":"advanced"} #TODO make this global
        author = input_data.get('author')
        if not Admin().getBy(username=author):
            return response(400, "author is not an admin, check the username", [])
        # Reads the cases from the uploaded files and decode the byte into a unicode string,
        # before saving it into the database
        if input_data.get('testcases') is not None: 
            testcases = input_data['testcases'].read().decode("utf-8")  
            input_data['testcases'] = testcases 
        else:
            input_data_plain['testcases'] = testcases 
        if input_data.get('answercases') is not None: 
            answercases = input_data['answercases'].read().decode("utf-8")  
            input_data['answercases'] = answercases 
        else:
            input_data['answercases'] = input_data_plain['answercases']
        if input_data.get('samplecases') is not None: 
            samplecases = input_data['samplecases'].read().decode("utf-8")  
            input_data['samplecases'] = samplecases 
        else:
            input_data['samplecases'] = input_data_plain['samplecases'] 
        if input_data.get('sampleanswercases') is not None: 
            sampleanswercases = input_data['sampleanswercases'].read().decode("utf-8")  
            input_data['sampleanswercases'] = sampleanswercases 
        else:
            input_data['sampleanswercases'] = input_data_plain['sampleanswercases']
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

        return response(400, "Problem not updated, check the problemid", [])              

class GetAllProblemTags(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self): 

        data = Problem().getBy(_id="tags")
        if data:
            tags = data.get("problemtags")
            return response(200, "Success", tags)
        
        default_tags = ['dfs','bfs','sorting','hashmap','constructive algorithm', 'greedy', 'recursion', 'graph']
        return response(200, "Default tags", default_tags)
    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self, problemid):
        return response(300, "Use a POST Request", [])

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
        if not ProblemInstance(pb).isValid():
            return response(400, 'Problem does not meet specification', [])
         
        params = {"status": 1, 'solvedby':[]} # add a new field `solvedby` to indicate all users that have solved a problem
        if Problem().update(params=params, _id=ObjectId(input_data['prblmid'])):
            return response(200, "Problem submitted", [])     

        return response(400, "Problem not submitted", [])     

class DeleteProblem(Resource):
    @jwt_required
    def delete(self):
        data = delete_problem_parser.parse_args()
        prblmid = data.get("prblmid")
        author = data.get('author')
        try:
            ObjectId(prblmid)
        except :
            return response(400, "Invalid ID", [])

        pb = Problem().getBy(_id=ObjectId(prblmid))
        if not pb:
            return response(400, "Problem not found", [])
        if author != pb.get('author'): 
            return response(400, "not the author of the problem", [])  

        if Problem().deleteOne(_id=ObjectId(prblmid)):
            return response(200, "Problem deleted Successfully", [])
        
        return response(400, "Unable to delete problem, problem with that id might not exist", [])