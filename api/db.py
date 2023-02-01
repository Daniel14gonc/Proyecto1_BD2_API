from flask_pymongo import pymongo
import os

CONNECTION_STRING = os.getenv("CONN_STRING")

client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('proyecto1')