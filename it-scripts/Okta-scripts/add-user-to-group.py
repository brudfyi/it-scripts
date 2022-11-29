#on command line before running script pip install requests Flask flask-cors pyOpenSSL Flask-Login okta-jwt-verifier

import time
import datetime
import json
import requests
import time
from datetime import datetime
#import okta_jwt_verifier

groupID = '00gam39fbyOH6yNz5357'
api_key = <API KEY IN 1PASS>
headers = {'Authorization': 'SSWS {}'.format(api_key), 'Accept': 'application/json', 'Content-Type':'application/json'}

okta_url = 'https://axiomzenportfolio.okta.com/api/v1/'
users_url = 'https://axiomzenportfolio.okta.com/api/v1/users'

response = requests.get('{}?limit=200'.format(users_url), headers = headers)
users = []

if response.status_code == 200:
    users = response.json()
    if len(users) == 200:
        last_user_id = users[-1]['id']
        response = requests.get('{}?filter=status%20eq%20%22ACTIVE%22&limit=200&after={}'.format(users_url, last_user_id), headers = headers)
        if response.status_code == 200:
            users = users + response.json()
        else:
            print(response.content)
            print(response)
else:
    print(response.content)
    print(response)

n = time.time()

for user in users:
    if 'profile' in user and 'startDate' in user['profile']:
        t = time.mktime(datetime.strptime(user['profile']['startDate'], "%Y-%m-%d").timetuple())
        if t <= n:
            print(user['id'])
            url = 'https://axiomzenportfolio.okta.com/api/v1/groups/{}/users/{}'.format(groupID, user['id'])
            print(url)
            response = requests.put(url, headers = headers)
            if response.status_code != 200 and response.status_code != 204:
               print(response.content)
               print("Thats Doesn't work")
               exit()              
