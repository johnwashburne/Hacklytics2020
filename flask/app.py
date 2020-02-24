from flask import Flask, render_template, request, url_for
from model import Model
import pymongo
import json
import requests
from requests import Session
import pickle

m = Model()

password = json.load(open('mongo.json', 'r'))['password']
client = pymongo.MongoClient("mongodb+srv://john:{}@cluster0-9gcai.mongodb.net/test?retryWrites=true&w=majority".format(password))
db = client["hacklyticsdb"]
collection = db['hacklytics']

s = pickle.load(open("session.dat", "rb"))

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
    info['pk'] = int(sub['id'])

    return info


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/getTargets', methods=['GET'])
def get_targets():
    top20 = collection.find().sort([("proba", -1)]).limit(20)
    docs = []
    a = '''<h2>Most Likely to Follow Back'''
    for doc in top20:
        docs.append(doc)
        a += """<div class="row" style="padding: 10px;">
                        <div class="col-2">
                        """
        a += '''<img height=150 width=150 style="border-radius: 100%;" src="{}"/></div>
                <div class="col-8">
                          <div class="row">'''.format(doc['profile_pic'])
        a += '''<h3><strong>{}</strong></h3></div>
                    <div class="row">'''.format(doc['username'])
        a += '''<h4>Probability: {}%</h4></div></div></div>'''.format(doc['proba'])

    return a
    

@app.route('/targets')
def targets():
    return render_template('targets.html')

@app.route('/results', methods=['POST'])
def results():
    if request.method == 'POST':
        response = request.form.to_dict()
        username = response['username']
        docs = collection.find({'username': username})
        flag = False
        
        if collection.count_documents({'username':username}) == 0:
            print('no')
            info = gather_data(username, s)
            flag = True
        else:
            print('yes')
            info = docs[0]
            
        followers = info['followers']
        following = info['following']
        verified = info['verified']
        private = info['private']
        post_count = info['post_count']
        mutual = info['mutual']
        
        highlight_count = info['highlight_count']
        recently_joined = info['recently_joined']
        ratio = followers / following
        profile_pic = info['profile_pic']
        if flag:
            proba = m.predict([[followers, following, private, verified,
                                post_count, mutual, highlight_count,
                                recently_joined, ratio]]) * 100
            proba = round(proba, 2)
            info['proba'] = proba
            collection.insert_one(info)
        else:
            proba = info['proba']
        
        
        f_x = m.follow_data['x']
        print(len(f_x))
        f_y = m.follow_data['y']
        f_z = m.follow_data['z']
        n_x = m.nonfollow_data['x']
        print(len(n_x))
        n_y = m.nonfollow_data['y']
        n_z = m.nonfollow_data['z']
        
        return render_template('results.html', username=username, proba=proba, followers=followers,
                               following=following, profile_pic=profile_pic, post_count=post_count,
                               f_x=f_x, f_y=f_y, f_z=f_z, n_x=n_x, n_y=n_y, n_z=n_z, mutual=mutual)
    return 'you are a failure'

if __name__ == '__main__':
    app.run()
