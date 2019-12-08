from flask_restful import Resource,reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity, get_raw_jwt
    )

from coderunner.taskqueue import queue
from coderunner.task import Task
from db.models import Problem
from bson.objectid import ObjectId
from coderunner.problem import ProblemInstance

run_code_parser = reqparse.RequestParser()
run_code_parser.add_argument('prblmid', help = 'This field cannot be blank. It also accept email', required = True)
run_code_parser.add_argument('usermail', help = 'This field cannot be blank', required = True)
run_code_parser.add_argument('codecontent', help = 'This field cannot be blank', required = True)
run_code_parser.add_argument('lang', help = 'This field cannot be blank', required = True)

run_code_status_parser = reqparse.RequestParser()
run_code_status_parser.add_argument('taskid', help = 'This field cannot be blank.', required = True)
run_code_status_parser.add_argument('lang', help = 'This field cannot be blank.', required = True)
run_code_status_parser.add_argument('prblmid', help = 'This field cannot be blank', required = True)
run_code_status_parser.add_argument('usermail', help = 'This field cannot be blank', required = True)



class RunCode(Resource):
    @jwt_required
    def post(self):
        input_data = run_code_parser.parse_args()

        problem_id=input_data["prblmid"] #get id
        problem = Problem.getBy(_id= ObjectId(problem_id))#fetch the actual problem from database with the problemId 
        if not problem:
            return {"code":"404","msg":"Invalid Problem ID","data":[]}

        user_mail=input_data["usermail"] #get email
        code_content=input_data["codecontent"] #get submitted code content
        language=input_data["lang"] #get submission language

        task_id=queue.generateID()
       
        task=Task(language,code_content,user_mail,ProblemInstance(problem),task_id)
        queue.add(task_id,task)

        return {"code":"200","msg":"Task started ","data":[task.toJson()]}

    @jwt_required
    def get(self):
        return  {"code":"300","msg":"Use A Post Request","data":[]}


class RunCodeStatus(Resource):
    @jwt_required
    def post(self):
        input_data = run_code_status_parser.parse_args()

        problem_id=input_data["prblmid"]
        problem= Problem.getBy(_id= ObjectId(problem_id))
        if not problem:
            return {"code":"404","msg":"Invalid Problem ID","data":[]}

        user_mail=input_data["usermail"]
        task_id=input_data["taskid"]
        language=input_data["lang"]

        task=queue.getById(task_id)

        if task is None:
            return {"code":"404","msg":"Task not found","data":[]}

        return {"code":"404","msg":"Task state is {} ".format(task.status()),"data":[task.toJson()]}

    @jwt_required
    def get(self):
        return  {"code":"300","msg":"Use A Post Request","data":[]}


