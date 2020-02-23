import json
import pickle
import os.path
import requests
import time
import pandas as pd
import os.path

# 500 requests in one hour until rate limitation from web api with delay of .25 seconds between requests

print("close the csv idiot")

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

s = pickle.load(open("session.dat", "rb"))

followers = json.load(open('followers.json', 'r'))
followings = json.load(open('followings.json', 'r'))


# create list of follower and following usernames
follower_users = []
for f in followers:
    follower_users.append(f['username'])

following_users = []
for f in followings:
    following_users.append(f['username'])


master_info = {}
count = 0
print(len(following_users))
for f in following_users[970:1000]:
    try:
        info = gather_data(f, s)
        print(info['username'], count)

        if f in follower_users:
            info['following_back'] = 1
        else:
            info['following_back'] = 0

        master_info[info['username']] = info
    except:
        print("error")
    time.sleep(1.5)
    count += 1


df = pd.read_json(json.dumps(master_info)).transpose()
if not os.path.isfile('data.csv'):
    df.to_csv('data.csv')
else:
    original  = pd.read_csv('data.csv', index_col=0)
    final = pd.concat([original, df], axis=0)
    final.to_csv('data.csv')

    
