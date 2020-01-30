from flask_restful import Resource,reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity, get_raw_jwt
    )
from db.models import Admin,Internships
from flask import request 
from bson.objectid import ObjectId
from flask_cors import  cross_origin


add_internship_parser = reqparse.RequestParser()
add_internship_parser.add_argument("admin",help="Admin username",required=True)
add_internship_parser.add_argument('title', help='', required=True)
add_internship_parser.add_argument('companyname', help='', required=True)
add_internship_parser.add_argument('location', help='', required=True)
add_internship_parser.add_argument('hiring', type=bool, help='', required=True)
add_internship_parser.add_argument('description', help='', required=True)
add_internship_parser.add_argument('link', help='', required=True)
add_internship_parser.add_argument('qualifications', help='', required=True)
add_internship_parser.add_argument('opentime', help='', required=True)
add_internship_parser.add_argument('closingtime', help='', required=True) 

get_internship_parser = reqparse.RequestParser()
get_internship_parser.add_argument("uniqueid",help="Internsip ID",required=True) 



def response(code,msg,data,access_token=""):
    return {"code":code,"msg":msg,"data":data}

class AddInternship(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        return response(300, "Use a POST Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        data = add_internship_parser.parse_args()

        if not Admin().getBy(username=data["username"]):
            return response(400,"Username for admin not found",[])
        
        uid=Internships().addDoc(data)
        data["_id"]=str(uid) 

        return response(200,"Internship opportunity added",[]) 

class GetInternships(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        return response(300, "Use a GET Request", [])

    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self): 

        include={"_id":1,"title":1,"companyname":1,"location":1,"hiring":1}
        data = list(Internships().getAll(params=include))
        for each in data:
            each["_id"] = str(each.get("_id"))

        return response(200,"Success",data) 

class ViewInternship(Resource):
    @jwt_required
    @cross_origin(supports_credentials=True)
    def get(self):
        data = get_internship_parser.parse_args()

        uid = data['uniqueid']
        exclude={"_id":0}
        data=data=Internships().getBy(params=exclude, _id=ObjectId(uid))
        if not data:
            return response(400,"Not found",[])

        return response(200, "Success", data)

    @jwt_required
    @cross_origin(supports_credentials=True)
    def post(self):
        return response(300, "Use a GET Request", [])
        