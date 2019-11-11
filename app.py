"""
Entry Point to the entire application. it is recommeded to keep this file as simple as possible.

"""


from flask import Flask
from flask_restful import Api
from api.access.user import UserAPI

app=Flask(__name__)
api=Api(app)


@app.route("/")
def index():
    return "Hello !!"
api.add_resource(UserAPI, '/<string:id>')

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)