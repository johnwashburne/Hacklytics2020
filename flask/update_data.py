import pandas as pd
import json
import pickle
import time
import os.path
import requests
from InstagramAPI import InstagramAPI

credentials = json.load(open('instagram.json', 'r'))
api = InstagramAPI(credentials['username'], credentials['password'])
api.login()

followers = api.getTotalFollowers(api.username_id)
followings = api.getTotalFollowings(api.username_id)

json.dump(followers, open('followers2.json', 'w'))
json.dump(followings, open('followings2.json', 'w'))



s = pickle.load(open("session.dat", "rb"))

# fix encode errors
def BMP(s):
    return "".join((i if ord(i) < 10000 else '\ufffd' for i in s))

def gather_data(username, s):
    if not isinstance(s, requests.Session):
        raise TypeError('Must pass a session object')

    response = s.get('https://www.instagram.com/{}/?__a=1'.format(username))
    print(response)
    response = response.json()
    info = {}
    sub = response['graphql']['user']
    info['bio'] = BMP(sub['biography'])
    info['followers'] = sub['edge_followed_by']['count']
    info['following'] = sub['edge_follow']['count']
    info['private'] = sub['is_private']
    info['verified'] = sub['is_verified']
    info['post_count'] = sub['edge_owner_to_timeline_media']['count']
    info['mutual'] = sub['edge_mutual_followed_by']['count']
    info['highlight_count'] = sub['highlight_reel_count']
    info['recently_joined'] = sub['is_joined_recently']
    info['username'] = username

    return info

follower_users = []
for f in followers:
    follower_users.append(f['username'])

following_users = []
for f in followings:
    following_users.append(f['username'])

if os.path.isfile('data.csv'):
    df = pd.read_csv('data.csv', index_col=0)
else:
    df = pd.DataFrame()

master_info = {}
count = 0

print(len(following_users))
for f in following_users:
    if not str(f) in df.index:
        info = gather_data(f, s)
        print(info['username'], count)

        if f in follower_users:
            info['following_back'] = 1
        else:
            info['following_back'] = 0

        master_info[info['username']] = info
        
        time.sleep(1.5)
        count += 1


df = pd.read_json(json.dumps(master_info)).transpose()
if not os.path.isfile('data.csv'):
    df.to_csv('data.csv')
else:
    original  = pd.read_csv('data.csv', index_col=0)
    final = pd.concat([original, df], axis=0)
    final.to_csv('data.csv')
