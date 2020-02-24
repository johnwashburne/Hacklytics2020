import json
import pymongo
import datetime
import os.path
import time
from InstagramAPI import InstagramAPI
import schedule



credentials = json.load(open('instagram.json', 'r'))
api = InstagramAPI(credentials['username'], credentials['password'])
api.login()

followers = json.load(open('followers.json', 'r'))
follower_list = []
for f in followers:
    follower_list.append(f['username'])

followings = json.load(open('followings.json', 'r'))
following_list = []
for f in followings:
    following_list.append(f['username'])

password = json.load(open('mongo.json', 'r'))['password']
client = pymongo.MongoClient("mongodb+srv://john:{}@cluster0-9gcai.mongodb.net/test?retryWrites=true&w=majority".format(password))
db = client["hacklyticsdb"]
collection = db['hacklytics']
log = db['log']


def task():
    # find accounts that need to be unfollowed
    # {'pk': 3489720, 'username': adsfdsaf, 'dt': }
    for doc in log.find():
        td = datetime.datetime.now() - datetime.datetime.strptime(doc['dt'],'%Y-%m-%d %H:%M:%S.%f')
        if td.days > 3 and i['username'] not in follower_list:
            api.unfollow(doc['pk'])
            time.sleep(5)
            log.delete_one({'_id': doc['id']})

    # find top two accounts from mongo
    docs = collection.find().sort('proba', -1)
    count = 0
    for doc in docs:
        if doc['username'] not in follower_list and doc['username'] not in following_list:
            api.follow(doc['pk'])
            print('followed {}'.format(doc['pk']))
            time.sleep(5)
            log.insert_one({'pk': doc['pk'], 'dt': str(datetime.datetime.now())})
            count += 1
            if count == 3:
                break

schedule.every().hour.do(task)
while True:
    schedule.run_pending()
    time.sleep(2)
            


