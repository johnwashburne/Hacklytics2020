from InstagramAPI import InstagramAPI
import json

credentials = json.load(open('instagram.json', 'r'))
api = InstagramAPI(credentials['username'], credentials['password'])
api.login()

followers = api.getTotalFollowers(api.username_id)
followings = api.getTotalFollowings(api.username_id)

json.dump(followers, open('followers2.json', 'w'))
json.dump(followings, open('followings2.json', 'w'))

