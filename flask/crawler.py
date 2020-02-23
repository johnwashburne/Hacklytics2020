import pymongo
import requests
import pickle
import schedule
import json
import time
from model import Model
from InstagramAPI import InstagramAPI

class Crawler:
    def __init__(self):
        self.users = []
        self.count = 0

c = Crawler()
m = Model()

credentials = json.load(open('instagram.json', 'r'))
api = InstagramAPI(credentials['username'], credentials['password'])
api.login()

password = json.load(open('mongo.json', 'r'))['password']
client = pymongo.MongoClient("mongodb+srv://john:{}@cluster0-9gcai.mongodb.net/test?retryWrites=true&w=majority".format(password))
db = client["hacklyticsdb"]
collection = db['hacklytics']

s = pickle.load(open("session.dat", "rb"))
user_seed = 1906447189


def parse_seed_followers(s_f):
    c.users = []
    for i in seed_followers:
        flag = True
        for f in followings:
            if f['username'] == i['username']:
                flag = False
                break

        if collection.count_documents({'username': i['username']}) != 0:
            flag = False

        if flag:
            c.users.append(i)
            
    return c.users


def gather_data(username, s):
    if not isinstance(s, requests.Session):
        raise TypeError('Must pass a session object')

    response = s.get('https://www.instagram.com/{}/?__a=1'.format(username))
    print(response)
    response = response.json()
    #response = json.load(open('sample.json', 'r'))
    info = {}
    sub = response['graphql']['user']
    info['followers'] = int(sub['edge_followed_by']['count'])
    info['username'] = username
    info['following'] = int(sub['edge_follow']['count'])
    info['private'] = int(sub['is_private'])
    info['verified'] = int(sub['is_verified'])
    info['post_count'] = int(sub['edge_owner_to_timeline_media']['count'])
    info['mutual'] = int(sub['edge_mutual_followed_by']['count'])
    info['highlight_count'] = int(sub['highlight_reel_count'])
    info['recently_joined'] = int(sub['is_joined_recently'])
    info['profile_pic'] = sub['profile_pic_url_hd']
    info['ratio'] = info['followers'] / info['following']

    proba = m.predict([[info['followers'], info['following'], info['private'],
                                info['verified'], info['post_count'], info['mutual'],
                                info['highlight_count'], info['recently_joined'],
                                info['ratio']]]) * 100
    info['proba'] = round(proba, 2)

    return info


def task():
    print('starting task')
    if len(c.users) == 0:
        docs = collection.aggregate([{"$sample": { "size": 1 } }])
        doc = None
        for d in docs:
            doc = d
            break

        seed_followers = api.getTotalFollowers(doc['pk'])
        c.users = parse_seed_followers(seed_followers)
    c.count += 1

    user = c.users.pop(0)
    print(user['username'])
    collection.insert_one(gather_data(user['username'], s))
    

followings = json.load(open('followings.json', 'r'))
seed_followers = api.getTotalFollowers(1906447189)
c.users = parse_seed_followers(seed_followers)
print(len(c.users))

schedule.every(36).seconds.do(task)

print('entering loop')
time.sleep(7200)
while True:
    schedule.run_pending()
    if c.count > 300:
        break
    
    time.sleep(1)

        

