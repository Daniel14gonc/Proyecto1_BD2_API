# using flask_restful
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import os
import db
  
# creating the flask app
app = Flask(__name__)

# creating an API object
api = Api(app)
  
# making a class for a particular resource
# the get, post methods correspond to get and post requests
# they are automatically mapped by flask_restful.
# other methods include put, delete, etc.

class User(Resource):

    def get(self):
        print(os.getenv('COMPOSER'))
        return jsonify({"code": "200"})

    def post(self):
        try:
            data = request.get_json()
            db.db.users.insert_one(data)
            return jsonify({"message": "201"})
        except:
            return jsonify({"message": "400"})
  

class Tweet(Resource):

    def post(self):
        try:
            data = request.get_json()
            db.db.tweets.insert_one(data)
            return jsonify({"message": "201"})
        except:
            return jsonify({"message": "400"})

# adding the defined resources along with their corresponding urls
api.add_resource(User, '/user/')
api.add_resource(Tweet, '/tweet/')

  
# driver function
if __name__ == '__main__':
  
    app.run(debug = True)