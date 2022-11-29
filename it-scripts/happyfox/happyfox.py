#!/usr/local/bin/python3
#
# User /bin/python3 for typical systems

import json
import requests
import time
import os
import re
import math
import string
import pprint

api_count = 0
okta_base = 'https://axiomzenportfolio.okta.com'
api_base = 'https://dapperlabs.happyfox.com'
okta_api_key = '00kyBm5GwUiO5xBzpiE1u2vcjHaP9qZlU4K7S_zh5h'
api_key = '6b0bf59caa42416d8730249f579ff845'
api_auth_code = '2d5054084631450eaef9ae4132fcb69c'
okta_headers = {'Authorization': 'SSWS {}'.format(okta_api_key), 'Accept': 'application/json', 'Content-Type':'application/json'}

group_mappings = [
    {'hf_id': 9, 'okta_name': 'Dapper Collectives', 'access_tickets': False}
]

user_mappings = [
    {'hf_id': 1, 'okta_name': 'GitHub Username'}
]


def hf_api_request(endpoint, payload = False, m = False):
    url = '{}{}'.format(api_base, endpoint)
    auth = (api_key, api_auth_code)
    if payload:
        headers = {'Content-Type': 'application/json'}
        res = False
        # res = requests.post(url, auth = auth, data = json.dumps(payload), headers = headers)
    else:
        res = requests.get(url, auth = auth)
    
    return res.json()

def get_okta_groups(group_name = False):
    url = "{}/api/v1/groups".format(okta_base)
    response = requests.get(url, headers = okta_headers)
    if response.status_code == 200:
        current = response.json()
        if not group_name:
            return current
        else:
            for group in current:
                if group['profile']['name'] == group_name:
                    return group

            return False
    else:
        print("Okta user groups request failed with error {}".format(response.text))
        return False

def get_okta_users_for_group(group_name):
    group = get_okta_groups(group_name)
    if group:
        group_id = group['id']
        url = "{}/api/v1/groups/{}/users".format(okta_base, group_id)
        response = requests.get(url, headers = okta_headers)
        if response.status_code == 200:
            current = response.json()
            return current
        else:
            print("Okta users for group request failed with error {}".format(response.text))
            return False
    else:
        print("Could not retrieve Okta group with the name {}".format(group_name))
        return False

def get_okta_users(previous=[], limit=200):
        after = ''
        if len(previous) != 0:
            after = '&after={}'.format(previous[-1]['id'])
        url = "{}/api/v1/users?filter=status%20eq%20%22ACTIVE%22{}&limit={}".format(okta_base, after, limit)
        response = requests.get(url, headers = okta_headers)
        if response.status_code == 200:
            current = response.json()
            count = len(current)
            if len(previous) != 0:
                current = previous + current
            if count == limit and len(current) < 1000:
                # return get_okta_users(current, limit)
                return current
            else:
                return current
        else:
            print("Okta user list request failed with error {}".format(response.text))
            return previous

hf_users = hf_api_request('/api/1.1/json/users/')
okta_users = get_okta_users([], 5)

idx = 0
for group_mapping in group_mappings:
    emails = []
    members = get_okta_users_for_group(group_mapping['okta_name'])
    if members:
        for member in members:
            emails.append(member['profile']['login'])
    group_mappings[idx]['emails'] = emails
    idx = idx + 1


def get_okta_user(username):
    for okta_user in okta_users:
        if okta_user['profile']['login'] == username:
            return okta_user
    return False

def is_user_group_member(user_id, group_id):
    for hf_user in hf_users['data']:
        if hf_user['id'] == user_id:
            for group in hf_user['contact_groups']:
                if group['id'] == group_id and group['access_all_tickets_in_group']:
                    return True
    return False

def can_user_access_tickets_for_group(user_id, group_id):
    for hf_user in hf_users['data']:
        if hf_user['id'] == user_id:
            for group in hf_user['contact_groups']:
                if group['id'] == group_id:
                    return True
    return False

if 'data' in hf_users and okta_users:
    for hf_user in hf_users['data']:
        print(hf_user['name'])
        okta_user = get_okta_user(hf_user['email'])
        for group_mapping in group_mappings:
            print(group_mapping['okta_name'])
            if hf_user['email'] in group_mapping['emails'] and not is_user_group_member(hf_user['id'], group_mapping['hf_id']):
                print('Need to add {} to {}'.format(hf_user['email'], group_mapping['okta_name']))
                payload =  {'contact': hf_user['id'], 'access_tickets': group_mapping['access_tickets']}
                # res = hf_api_request('/api/1.1/json/contact_group/{}/update_contacts/'.format(group_mapping['hf_id']), payload)




# users['data'][]
# ['contact_groups'][]['access_all_tickets_in_group']
# ['contact_groups'][]['id']
# ['contact_groups'][]['name']
# ['email']
# ['id']
# ['name']
# [''custom_fields'][]['id']
# [''custom_fields'][]['value'] (None)


# pprint.pprint(users['data'])
