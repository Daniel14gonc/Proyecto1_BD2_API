from flask import jsonify, request
from flask_restful import Resource
from bson.json_util import dumps
from json import loads
from datetime import datetime
from bson.objectid import ObjectId
import pymongo
import db



class User(Resource):

    def __init__(self):
        self.collection = db.db['users']

    def get(self):
        return jsonify({"code": "200"})

    def post(self):
        try:
            data = request.get_json()
            print(data)
            self.collection.insert_one(data)
            return jsonify({"message": "success"})
        except:
            return jsonify({"message": "error"})

class UserAuthenticator(Resource):

    def __init__(self):
        self.collection = db.db['users']

    def post(self):
        try:
            data = request.get_json()
            query_result = self.collection.find_one({"username": data["username"]}, {"_id": 0, "password": 1})
            if query_result["password"] == data["password"]:
                return jsonify({"message": "200"})
            else:
                return jsonify({"message": "401"})
        except:  
            return jsonify({"message": "400"})

class Like(Resource):
    
    def put(self):
        pass

class Comments(Resource):

    def __init__(self):
        self.collection = db.db['tweets']
    
    def get(self):
        try:
            data = request.headers
            pipeline = [
                {
                    "$match": {
                    '_id': ObjectId(data["id_tweet"])
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "comments": 1
                    }
                }
            ]
            query_result = self.collection.aggregate(pipeline)
            return loads(dumps(query_result))
        
        except:
            return jsonify({"message": "400"})

class Tweet(Resource):

    def __init__(self):
        self.collection = db.db['tweets']


    def get(self):
        try:
            data = request.headers

            print(data)

            pipeline = [
                {
                    "$project": {
                        "_id": 1,
                        "username": 1,
                        "text": 1,
                        "date": 1,
                        "likes": 1,
                        "comments": 1,
                        "comments_count": {"$size": '$comments'}
                    }
                },
                {
                    "$sort": {
                        "date": pymongo.DESCENDING
                    }
                },
                {
                    "$limit": int(data["limite"])
                }
            ]
            # query_result = self.collection.find().sort("date", -1).limit(int(data["limit"]))
            query_result = self.collection.aggregate(pipeline)
            
            return loads(dumps(query_result))
        except:
            return jsonify({"message": "400"})

    def put(self):
        data = request.get_json()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(data)
        self.collection.update_one(
            {"_id": ObjectId(data["id_tweet"])}, 
            {"$push": {"comments": {"username_comment": data["user"], "text_comment": data["content"], "date_comment": now}}}
        )

        data = {"username_comment": data["user"], "text_comment": data["content"], "date_comment": now}

        return jsonify(data)

    def post(self):
        try:
            data = request.get_json()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data['date'] = now
            data['likes'] = 0
            data['comments'] = []

            self.collection.insert_one(data)
            data['comments_count'] = 0
            return loads(dumps(data))
        except:
            return jsonify({"message": "400"})