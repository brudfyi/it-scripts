#!/usr/bin/python
########## This script is a gongshow, I stole it from online and have been using it to reference/dick around with github org tasks

# Exports a CSV of repo names, readme files, and the license of the project.

from __future__ import print_function
import requests
import json
import settings
from urlparse import urlparse, parse_qs
import sys

def getLastPage(link_header):
  if link_header is None:
    return 1
  links = link_header.split(',')
  for link in links:
    link = link.split(';')
    if link[1].strip() == 'rel="last"':
      # Trim it for garbage, and get the url params out.
      link_data = parse_qs(link[0].strip(' <>').split('?')[1])
      last_page = int(link_data['page'][0])
      return last_page
  return 0

github_urls = {
  'repos': 'https://api.github.com/orgs/{org}/repos', # GET
  'teams': 'https://api.github.com/orgs/{org}/teams?per_page=100', # GET
  'teamrepo': 'https://api.github.com/teams/{teamid}/repos/{org}/{repo}' # PUT
}

gh_payload = {'access_token': settings.GITHUB_TOKEN}


# Get our teams, let the user pick one.

teams_r = requests.get(github_urls['teams'].format(org=settings.GITHUB_ORG), gh_payload)
teams = json.loads(teams_r.text)

team_map = {}

for team in teams:
  team_map[team['id']] = team['name']

print(team_map.values())

team = ''

while team == '':
  print('Pick a team:')
  print(', '.join(team_map.values()))
  team = raw_input('? ')
  if team not in team_map.values():
    team = ''

team_id = team_map.keys()[team_map.values().index(team)]

# Get a list of all GitHub projects.

# First off, how many pages do we have?

# Get the first page.
head = requests.get(github_urls['repos'].format(
  org=settings.GITHUB_ORG), gh_payload)

# Look for the last page link in the headers
last_page = getLastPage(head.headers.get('link'))

if last_page != 0:

  for page in range(1, last_page + 1):

    repo_payload = gh_payload.copy()
    repo_payload['page'] = page

    # headers = { 'Accept': 'application/vnd.github.drax-preview+json' }
    headers = {}

    r = requests.get(github_urls['repos'].format(
      org=settings.GITHUB_ORG), repo_payload, headers=headers)

    existing_projects = json.loads(r.text)

    for existing_project in existing_projects:
      print('Project: ' + existing_project['name'])

      team_payload = gh_payload.copy()
      team_payload['permission'] = 'push'
      repo_r = requests.put(github_urls['teamrepo'].format(
        org=settings.GITHUB_ORG,
        repo=existing_project['name'],
        teamid=team_id
      ), params=gh_payload, data=json.dumps(team_payload))

  print('Done.')
else:
  print('Didn\'t find any existing projects.', file=sys.stderr)
