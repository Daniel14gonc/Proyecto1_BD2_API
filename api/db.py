from flask_pymongo import pymongo
import os

CONNECTION_STRING = os.getenv("CONN_STRING") # atlas
CONNECTION_STRING = "mongodb://localhost:27017" # local

client = pymongo.MongoClient(CONNECTION_STRING)
db = client["proyecto1"]