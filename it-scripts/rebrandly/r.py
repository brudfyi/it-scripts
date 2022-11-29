#!/usr/bin/env python3

import requests
import json
import dotenv
import pandas

### config

dotenv.load() # .env
API_KEY=dotenv.get('API_KEY')
DOMAIN=dotenv.get('DOMAIN')
WORKSPACE_ID=dotenv.get('WORKSPACE_ID')
FILE=dotenv.get('FILE')

columns = ['SLASH_TAG','DEST_URI','LINK_DESC']
data = pandas.read_csv(FILE, names=columns)

requestHeaders = {
  "Content-type": "application/json",
  "apikey": API_KEY,
  "workspace": WORKSPACE_ID
}

def createLink(slashTag, uri):
  print("Creating SlashTag: [",slashTag,"], URI: ",uri)

  linkRequest = {
  "destination": uri
  , "domain": { "fullName": DOMAIN}
  , "slashtag": slashTag
  # , "title": "a title"
  }

  r = requests.post("https://api.rebrandly.com/v1/links", 
      data = json.dumps(linkRequest),
      headers=requestHeaders)

  if (r.status_code == requests.codes.ok):
      link = r.json()
      print(" - Long URL was %s, short URL is %s" % (link["destination"], link["shortUrl"]))
  else:
      print("well, that didn't work - here's the req and resp:")
      print(linkRequest)
      print(r)
  
for index, row in data.iterrows():
    if index != 0:
        row = row.tolist()
        slashTag = row[0]
        uri = row[1]
        
        createLink(slashTag,uri)

