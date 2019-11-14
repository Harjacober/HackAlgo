"""
Entry Point to the entire application. it is recommeded to keep this file as simple as possible.

"""


from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from api.access.user import UserAPI
from api.resources.regapi import AdminRegistration,UserRegistration,AdminLogin,UserLogin


app=Flask(__name__)
app.config.from_object('config')

api=Api(app)
jwt = JWTManager(app)


@app.route("/")
def index():
    return "Hello !!"

api.add_resource(AdminRegistration, '/nimdareg/')
api.add_resource(UserRegistration, '/userreg/')
api.add_resource(AdminLogin, '/nimdalogin/')
api.add_resource(UserLogin, '/userlogin/')
api.add_resource(UserAPI, '/<string:id>')

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)