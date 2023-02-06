from flask import jsonify, request
from flask_restful import Resource
from bson.json_util import dumps
from json import loads
from datetime import datetime
from bson.objectid import ObjectId
import pymongo
import gridfs
import base64
from random import randint
import db

class Image(Resource):

    def __init__(self):
        self.database = db.db
        
    def get(self):
        try:
            fs = gridfs.GridFS(self.database)
            file = fs.find_one({'filename': "P6.jpeg"})
            image = file.read()
            encoded_string = base64.b64encode(image)
            return jsonify({"imagen": encoded_string.decode()})
        except:
            return jsonify({"message": "400"})

class User(Resource):

    def __init__(self):
        self.collection = db.db['users']

    def get(self):
        return jsonify({"code": "200"})
        
    def post(self):
        try:
            data = request.get_json()
            query_result = self.collection.find({"username": data["username"]})
            results = list(query_result)
            if len(results) == 0:
                self.collection.insert_one(data)
                return jsonify({"message": "200"})
            else:
                return jsonify({"message": "409"})
        except Exception as e:
            print(e)
            return jsonify({"message": "400"})

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

    def __init__(self):
        self.collection = db.db['tweets']

    def get(self):
        try:
            data = request.headers
            query = self.collection.find_one({"_id": ObjectId(data["id_tweet"])}, {"_id": 0, "likes": 1})
            return jsonify(query)
        except:
            return jsonify({"message": "400"})
    
    def put(self):
        try:
            data = request.get_json()
            self.collection.update_one(
                {"_id": ObjectId(data['id_tweet'])},
                {
                    "$inc": {"likes": 1}
                }
            )
            return {"message": "200"}
        except:
            return {"message": "400"}

class Comments(Resource):

    def __init__(self):
        self.collection = db.db['tweets']
        
    def delete(self):
    
    
        try: 
            data = request.headers
            pipeline =[
                { "comments": 
                    { 
                        "$elemMatch": { 
                            "text": data["text"], 
                            "user": data["user"],
                            "date": data["date"] 
                            } 
                    }
                },
                { "$pull": { "comments": { 
                            "text": data["text"], 
                            "user": data["user"],
                            "date": data["date"] 
                    } 
                }   
                }
                
            ]
            return jsonify({"message": "200"})
        except: 
            return jsonify({"message": "400"})

            
    
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
        self.database = db.db
        self.fs = gridfs.GridFS(self.database)
        
    def delete(self):
        try:
            data = request.headers
            self.collection.delete_one({"_id": ObjectId(data["id_tweet"])})
            return jsonify({"message": "200"})
        except: 
            return jsonify({"message": "400"})


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
            result = []
            for element in query_result:
                random = randint(1, 10)
                file = self.fs.find_one({'filename': "P"+str(random)+".jpeg"})
                image = file.read()
                encoded_string = base64.b64encode(image)
                element["image"] = encoded_string.decode()
                result.append(element)
            
            return loads(dumps(result))
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


class Perfil(Resource):

    def __init__(self):
        self.collection = db.db['tweets']
    
    def get(self):
        try:
            data = request.headers
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
                    "$match": { "username": data["name"]}
                },
                {
                    "$sort": { "date": pymongo.DESCENDING }
                },
                {
                    "$limit": int(data["limite"])
                }
                
                
            ]
            query_result = self.collection.aggregate(pipeline)
            return loads(dumps(query_result))
        
        except :
            return jsonify({"message": "400"})
