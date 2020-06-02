from flask_restful import Resource,reqparse
from flask_cors import  cross_origin
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity, get_raw_jwt
    )

from coderunner.taskqueue import queue
from coderunner.task import Task
from db.models import Problem,Submission,User,Admin
from bson.objectid import ObjectId
from bson.errors import InvalidId
from coderunner.problem import ProblemInstance
from werkzeug.datastructures import FileStorage
from utils.util import SupportedLanguages,response


run_code_parser = reqparse.RequestParser()
run_code_parser.add_argument('prblmid', help = 'This field cannot be blank. It also accept email', required = True) 
run_code_parser.add_argument('codecontent', help = 'This field cannot be blank', required = True)
run_code_parser.add_argument('codefile', type=FileStorage, location='files', required = False, store_missing=False)
run_code_parser.add_argument('lang', help = 'This field cannot be blank', required = True)
run_code_parser.add_argument('stype', help = 'This field cannot be blank', required = True) 

run_code_status_parser = reqparse.RequestParser()
run_code_status_parser.add_argument('taskid', help = 'This field cannot be blank.', required = True)
run_code_status_parser.add_argument('lang', help = 'This field cannot be blank.', required = True)
run_code_status_parser.add_argument('prblmid', help = 'This field cannot be blank', required = True)
run_code_status_parser.add_argument('userid', help = 'This field cannot be blank', required = True)



class RunCode(Resource): 
    """
    prepares submitted code and passes it to the :class: `Task` to run submission. 
    Handles adding of the partial submission info to the database.
    """
    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        input_data = run_code_parser.parse_args()

        problem_id=input_data["prblmid"] #get id
        problem = Problem().getBy(_id= ObjectId(problem_id))#fetch the actual problem from database with the problemId 
        if not problem:
            return response(400, "Invalid Problem Id", []) 

        currentUser = get_jwt_identity() #fromk jwt
        userid = currentUser.get("uid")
        user = User().getBy(_id=ObjectId(userid)) or Admin().getBy(_id=ObjectId(userid))
        if not user:
            return response(400,"User Id not found",{})

        task_id=queue.generateID()
        codecontent = input_data.get('codecontent')
        stype = input_data.get('stype')
        lang = input_data.get('lang')
        #check if programming language specified is supported
        if lang not in SupportedLanguages:
            return response(400, "Specified language not supported", [])
        codefile = input_data.get('codefile') 
        task=Task(lang,codecontent,userid,ProblemInstance(problem),task_id,stype,codefile)
        queue.add(task_id,task) 
        
        code=200
        if task.verdict!="Passed":
            code=400
        return response(code, "Task started", [task.toJson()]) 

    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        return response(300,"Use a POST REQUEST",[])


class RunCodeStatus(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        input_data = run_code_status_parser.parse_args()

        problem_id=input_data["prblmid"]
        problem= Problem().getBy(_id= ObjectId(problem_id))
        if not problem:
            return response(400, "Invalid Problem Id", []) 

        user_id=input_data.get("userid")
        task_id=input_data.get("taskid")
        language=input_data.get("lang")

        task=queue.getById(task_id)
 
        if task is None:
            return response(400, "Task not found", [])  

        return response(200, "Task state is {} ".format(task.status()), [task.toJson()]) 

    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        return response(300,"Use a POST REQUEST",[])


