import pymongo
import json

password = json.load(open('mongo.json', 'r'))['password']
client = pymongo.MongoClient("mongodb+srv://john:{}@cluster0-9gcai.mongodb.net/test?retryWrites=true&w=majority".format(password))
db = client["hacklyticsdb"]
collection = db['hacklytics']


docs = collection.aggregate([{"$sample": { "size": 1 } }])
doc = None
for d in docs:
    doc = d
