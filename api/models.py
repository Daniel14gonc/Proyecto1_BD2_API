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
import re
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


class TweetsPerYear(Resource):

    def __init__(self):
        self.collection = db.db['tweets']

    def get(self):
        data = request.headers
        pipeline = [
            {
                "$match": {
                    "userid": ObjectId(data["userId"])
                }
            },
            {
                "$project": {
                "year": { "$year": { "$dateFromString": { "dateString": "$date", "format": "%Y-%m-%d %H:%M:%S" } } }
            }
            },
            {
                "$group": {
                    "_id": "$year",
                    "count": { "$sum": 1 }
                }
            },
            {
                "$sort": {"_id": 1}
            },
            {
                "$limit": 10 
            }
        ]

        query_result = self.collection.aggregate(pipeline)
        return loads(dumps(query_result))


class User(Resource):

    def __init__(self):
        self.collection = db.db['users']
        self.db = db.db

    def get(self):
        return jsonify({"code": "200"})
        
    def post(self):
        #try:
        data = request.get_json()
        print(data)
        query_result = self.collection.find({"username": data["username"]})
        results = list(query_result)
        if len(results) == 0:
            query_result = self.collection.insert_one(data)
            query_result = self.collection.find_one({"username": data["username"]})
            
            query_result = loads(dumps(query_result))
            print(query_result)
            return jsonify({"message": "200", "userId": str(query_result["_id"]["$oid"])})

        else:
            return jsonify({"message": "409"})
        #except Exception as e:
            #return jsonify({"message": "400"})
        
    def delete(self):
        try:
            data = request.get_json()
            id = data["id"]
            user = data["user"]
            temp_collection = self.db["tweets"]
            requestUser = [pymongo.DeleteOne({"_id": ObjectId(id)})]
            requestsTweets = [
                pymongo.DeleteMany({"userid": ObjectId(id)}),
                pymongo.UpdateMany({}, {"$pull": {"comments": {"username_comment": user}}})
            ]
            self.collection.bulk_write(requestUser)
            temp_collection.bulk_write(requestsTweets)
            return jsonify({"message": "200"})
        except:
            return jsonify({"message": "400"})
        
class LikesAnalytics(Resource):

    def __init__(self):
        self.collection = db.db['tweets']
    
    def get(self):
        try:
            data = request.headers
            pipeline = [
                {
                    "$match": {
                        "userid": ObjectId(data["userId"])
                    }
                },
                {
                    "$project": {
                    "likes": 1,
                    "year": { "$year": { "$dateFromString": { "dateString": "$date", "format": "%Y-%m-%d %H:%M:%S" } } }
                }
                },
                {
                    "$group": {
                        "_id": "$year",
                        "count": { "$sum": "$likes" }
                    }
                },
                {
                    "$sort": {"_id": 1}
                },
                {
                    "$limit": 10 
                }
            ]

            query_result = self.collection.aggregate(pipeline)
            return loads(dumps(query_result))
        except:
            return jsonify({"message": "400"})


        
class CountriesInteraction(Resource):

    def __init__(self):
        self.collection = db.db['tweets']
    
    def get(self):
        data = request.headers
        user = data["userID"]
        pipeline = [
            {
                "$match": {
                    "userid": ObjectId(user)
                }
            },
            {
                "$unwind": "$comments"
            },
            {
                "$project": {
                    "userid": 1,
                    "user_interaction": "$comments.username_comment"
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_interaction",
                    "foreignField": "username",
                    "as": "info"
                }
            },
            {
                "$project": {
                    "country": {"$first": "$info"}
                }
            },
            {
                "$project": {
                    "country": "$country.country"
                }
            },
            {
                "$group": {
                    "_id": "$country",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": 5
            }
        ]

        query_result = self.collection.aggregate(pipeline)

        return loads(dumps(query_result))

class Hashtags(Resource):

    def __init__(self):
        self.collection = db.db['tweets']

    def get(self):
        try:
            hashtag = re.compile("#", re.IGNORECASE)
            year = re.compile("2022", re.IGNORECASE)
            pipeline = [
                {
                    "$match": {
                        "text": {"$regex": hashtag},
                        "date": {"$regex": year}
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "text": {
                            "$substr": ["$text", {"$indexOfBytes": ["$text", "#"]}, {"$strLenCP": "$text"}]
                        }
                    }
                },
                {
                "$project": {
                        "text": {"$split": ["$text", " "]}
                }
                },
                {
                    "$unwind": "$text"
                },
                {
                    "$group": {
                        "_id": "$text",
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$match": {
                        "_id": {"$ne": ""}
                    }
                },
                {
                    "$sort": {"count": -1}
                },
                {
                    "$limit": 10
                }
            ]

            query_result = self.collection.aggregate(pipeline)

            return loads(dumps(query_result))
        
        except:
            return jsonify({"message": "400"})


class UserAuthenticator(Resource):

    def __init__(self):
        self.collection = db.db['users']

    def post(self):
        try:
            data = request.get_json()
            query_result = self.collection.find_one({"username": data["username"]}, {"_id": 1, "password": 1})
            if query_result["password"] == data["password"]:
                return jsonify({"message": "200", "userId": str(query_result["_id"])})
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
            
            self.collection.update_one(

                { 
                    
                    '_id': ObjectId(data["id_tweet"])
                    
                },
                { "$pull": { "comments": { 
                            "username_comment": data["user"],
                            "text_comment": data["text"],
                            "date_comment": data["date_C"]
                            } 
                        }   
                }
                
            ) 
            return jsonify({"message": "200"})
        except: 
            return jsonify({"message": "400"})

            
    
    def get(self):
        #try:
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
            },
            {
                "$unwind": "$comments"
            },
            {
                "$sort": {"comments.date_comment": pymongo.DESCENDING}
            },
            {
                "$group": {
                    "_id": "$_id",
                    "comments": {"$push": "$comments"}
                }
            },
            {
                "$unwind": "$comments"
            },
            {
                "$project": {
                    "user": "$comments.username_comment",
                    "text": "$comments.text_comment",
                    "date": "$comments.date_comment"
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user",
                    "foreignField": "username",
                    "as": "info"
                }
            },
            {
                "$project": {
                    "user": 1,
                    "text": 1,
                    "date": 1,
                    "info": {"$first": "$info"}
                }
            },
            {
                "$project": {
                    "user": 1,
                    "text": 1,
                    "date": 1,
                    "image": "$info.image"
                }
            }
        ]
        query_result = self.collection.aggregate(pipeline)
        return loads(dumps(query_result))
        
        #except:
            #return jsonify({"message": "400"})

class TweetComment(Resource):
    def __init__(self):
        self.collection = db.db['tweets']

    def post(self):
        data = request.get_json()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.collection.update_one(
            {"_id": ObjectId(data["id_tweet"])}, 
            {"$push": {"comments": {"username_comment": data["user"], "text_comment": data["content"], "date_comment": now}}}
        )

        data = {"user": data["user"], "text": data["content"], "date": now}

        return jsonify(data)

class Tweet(Resource):

    def __init__(self):
        self.collection = db.db['tweets']
        self.users = db.db['users']
        
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

            pipeline = [
                    {
                        "$lookup": {
                        "from": "users",
                        "localField": "userid",
                        "foreignField": "_id",
                        "as": "user"
                            }
                    },
                    {
                    "$unwind": "$user"
                    },
                    {
                        "$replaceRoot": {
                            "newRoot": {
                            "$mergeObjects": [
                            { "username": "$user.username","image": "$user.image" },
                            "$$ROOT"]
                            }
                        }
                    },
                    {
                        "$project": {
                        "_id": 1,
                        "text": 1,
                        "date": 1,
                        "likes": 1,
                        "comments": 1,
                        "comments_count": {"$size": '$comments'},
                        "username": 1,
                        "image": 1
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
                '''
                random = randint(1, 10)
                file = self.fs.find_one({'filename': "P"+str(random)+".jpeg"})
                image = file.read()
                encoded_string = base64.b64encode(image)
                element["image"] = encoded_string.decode()'''
                result.append(element)
            
            return loads(dumps(result))
        except:
            return jsonify({"message": "400"})

    def put(self):
        try:
            data = request.get_json()
            self.collection.update_one(
                {"_id": ObjectId(data["id_tweet"])}, 
                {"$set": 
                    {
                        "text": data["text"],
                        "likes": data["likes"]
                    }
                }
            )

            data = {"text": data["text"], "likes": data["likes"]}

            return jsonify(data)
        
        except:
            return jsonify({"message": "400"})

    def post(self):
        try:
            data = request.get_json()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data['date'] = now
            data['likes'] = 0
            data['comments'] = []
            data['userid'] = ObjectId(data['userid'])

            self.collection.insert_one(data)
            data['comments_count'] = 0
            return loads(dumps(data))
        except:
            return jsonify({"message": "400"})

class ValentinesDay(Resource):

    def get(self):
        pass

    def put(self):
        data = request.json()
        user = data["id"]
        checked = data["checked"]

        if checked:
            requests = [
                pymongo.UpdateOne(
                    {"_id": ObjectId(user)},
                    {
                        "$set": {"Valentine": checked}
                    }
                ),
                pymongo
            ]

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
                        "userid": 1,
                        "text": 1,
                        "date": 1,
                        "likes": 1,
                        "comments": 1,
                        "comments_count": {"$size": '$comments'}
                    }
                },
                {
                    "$match": { "userid": ObjectId(data["userId"])}
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
    
class Description(Resource):
    def __init__(self):
        self.collection = db.db['users']
    
    def get(self):
        try:
            data = request.headers
            query_result = self.collection.find_one({"username":data["username"]}, {"_id":0, "desciption":1, "image":1})
            return query_result
        except:
            return jsonify({"message":"400"})
        
    def put(self):
        try:
            data = request.get_json()
            print(data)
            self.collection.update_one(
                {"username": data["username"]}, 
                {"$set": 
                    {
                        "desciption": data["new_desc"]
                    }
                }
            )
            return jsonify({"message":"200"})
        except:
            return jsonify({"message":"400"})

class HomeImage(Resource):
    def __init__(self):
        self.collection = db.db['users']
    
    def get(self):
        try:
            data = request.headers
            query_result = self.collection.find_one({"username":data["username"]}, {"_id":0, "image":1})
            return query_result
        except:
            return jsonify({"message":"400"})
        
        
        
class AnalyticsComments(Resource):

    def __init__(self):
        self.collection = db.db['tweets']
             
    def get(self):
        try:
            data = request.headers
            pipeline = [
                {
                    "$project": {
                        "_id": 1,
                        "userid": 1,
                        "count_comments": {"$size": "$comments"}
                    }
                },
                {
                    "$match": {"userid": ObjectId(data["userId"])}
                },
                {
                    "$group": {
                        "_id": "$userid",
                        "total_comments": {"$sum": "$count_comments"}
                    }
                }   
            ]
            query_result = self.collection.aggregate(pipeline)
            return loads(dumps(query_result))
        
        except:
            return jsonify({"message": "400"})

class Fans(Resource):
    def __init__(self):
        self.collection = db.db['tweets']
    
    def get(self):
        try:
            data = request.headers
            pipeline = [
                { "$match": { "userid": ObjectId(data["userId"]) } },
                { "$unwind": "$comments" },
                { "$group": { "_id": "$comments.username_comment", "count": { "$sum": 1 } } }, 
                { "$sort": { "count": -1 } },
                {"$limit": 5},
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "_id",
                        "foreignField": "username",
                        "as": "info"
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "count": "$count",
                        "data": {"$first": "$info"}
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "count": "$count",
                        "image": "$data.image"
                    }
                }
            ]
            query_result = self.collection.aggregate(pipeline)
            return loads(dumps(query_result))
        except:
            return {"message":"400"}
        
        
