#!/usr/bin/env python3
#
# Manage VPN
#
#
# 2020-01-13 - bjm - initial scaffolding
#

import dotenv,json,requests,urllib3

#### config

dotenv.load() # .env
API_KEY = dotenv.get('API_KEY')
URI = dotenv.get('URI','https://10.1.0.100:8443')
DEBUG = dotenv.get('DEBUG','false')
STRICT_TLS = dotenv.get('STRICT_TLS','false')
UNIFI_USER = dotenv.get('UNIFI_USER')
UNIFI_PASSWORD = dotenv.get('UNIFI_PASSWORD')


HEADERS = {"Accept": "application/json",
           "Content-Type": "application/json"}

if (STRICT_TLS == 'false'):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#### REST endpoints used in script

ENDPOINT_LOGIN='/api/login'
ENDPOINT_SITES='/api/self/sites'

#### Static REST payloads

# TBC if needed

####


def log(*messages):
    if (DEBUG=='true'):
        for msg in messages:
            print("DEBUG -- ",msg,end="")
        print()

def send(endpoint,body="",headers=HEADERS,verify=False,method="GET"):
    print("Sending request [ " + endpoint + " ]")
    target=URI+endpoint
    log("target  [ "+target+" ]")
    log("headers [ ",headers," ]")
    log("body    [ "+json.dumps(body)+" ]")
    log(verify)
    try:
        if (method=="POST"):
            response=session.post(target,headers=headers,data=json.dumps(body),verify=verify)
        else:
            response=session.get(target,headers=HEADERS,verify=verify)
        log("Response: " + response)
    except:
        log("Exception from: "+target)
        log(response.headers)
        log(response.text)
    return(response)

###############################

session = requests.Session()

# do the login
TWOFACTOR=input("2FA token for " + UNIFI_USER + ": ")

BODY_LOGIN = {
    "username": UNIFI_USER,
    "password": UNIFI_PASSWORD,
    "remember": "true",
    "strict": "true",
    "ubic_2fa_token": TWOFACTOR
}


loginresult=send(ENDPOINT_LOGIN,body=BODY_LOGIN,method="POST")

getsitesresult=send(ENDPOINT_SITES)