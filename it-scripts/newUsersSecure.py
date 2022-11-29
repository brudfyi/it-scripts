# A script to create new users for the az portfolio
# Bit of a gongshow
# 
# Args: <A csv with the cols:
#                      email, firstname, lastname, gh handle, personal email>
#      github-api-key
# TODO:
# - Fix the github team invite piece, it appears correct but isn't working
import subprocess
import pandas
import argparse
import json
import requests
import string
import random
import os

parser = argparse.ArgumentParser()
parser.add_argument("csv_file")
#parser.add_argument("gh_key") BAD BOY
GH_KEY=os.getenv('API_KEY')
args = parser.parse_args()
colnames = ['email','first', 'last', 'gh', 'personal_email']
data = pandas.read_csv(args.csv_file, names=colnames)
char_set = string.ascii_uppercase + string.digits

gam_command = '/home/"yourdomian'/bin/gamadv-xtd3/gam'

# Some GSuite functions
def add_to_g(email, first, last, pemail, org):
    try:
        print("- Add {0} to {1}".format(email, org))
        subprocess.check_output([gam_command, 'select', org, 'create', 'user', 
            email, 'firstname', first, 'lastname', last, 'changepassword', 'on', 
            'notify', pemail])
    except:
        print("- FAILED to add {0} to {1}".format(email, org))
        raise
def change_gpass(email, pemail):
    random_pass = ''.join(random.sample(char_set*8, 8))
    if "@dapperlabs.com" in email:
        org = "dapper"
    elif "@axiomzen.co" in email:
        org = "az"
    elif "@zenhub.com" in email:
        org = "zenhub"
    try:
        print("- Password for {0} changed".format(email))
        subprocess.check_output([gam_command, 'select', org, 'update', 'user',
            email, 'password', random_pass, 'notify', pemail])
    except:
        print("- Password for {0} NOT changed".format(email))
        raise
def add_to_ggroup(email, org, group):
    try:
        print("- Add {0} to {1}@{2}".format(email, group, org))
        if org == 'axiomzen':
            org = 'az'
            subprocess.check_output(
                [gam_command, 'select', org, 'update', 'group', 
                group, 'add', 'member', 'user', email], 
                stderr=subprocess.STDOUT)
    except:
        print("- FAILED to add {0} to {1}@{2}".format(email, group, org))
        raise
def add_to_gcal(email, org, calendar_url):
    try:
        if org == 'axiomzen':
            org = 'az'
        subprocess.check_output([gam_command, 'select', org, 'calendar', 
            calendar_url, 'add', 'read', email, 'sendnotifications', 'false'])
        print("- Add {0} to {1}".format(email, calendar_url))
    except:
        print("- FAILED to Add {0} to {1}".format(email, calendar_url))
        raise

# Some setup for GitHub
gh_urls = {
  'memberships': 'https://api.github.com/orgs/{gh_org}/memberships/{gh_user}',
  'teams-get': 'https://api.github.com/orgs/{gh_org}/teams?per_page=200',
  'teams': 'https://api.github.com/teams/{gh_teamid}/memberships/{gh_user}',
}
gh_header = {'Authorization':'token {0}'.format(GH_KEY)}

def add_to_gh_org(fn, org, user):
    print("=========================================")
    print("Adding {user} to {org}")

    output = requests.put(gh_urls['memberships'].format(gh_org=org, 
        gh_user=user), headers=gh_header)
    print(output.json())

    print("Finished adding {user} to {org}")
    print("=========================================")

def add_to_gh_team(fn, org, user, teamid):
    print("=========================================")
    print("Adding {user} to TEAM ({teamid})")

    output = requests.put(gh_urls['teams'].format(gh_org=org, 
        gh_teamid=teamid, gh_user=user), headers=gh_header)
    print(output.json())

    print("Finished adding {user} to TEAM")
    print("=========================================")

print(data)

for index, row in data.iterrows():
    if index != 0:
        row = row.tolist()
        user_email = row[0]
        user_first = row[1]
        user_last = row[2]
        user_gh = row[3]
        personal_email = row[4]
        print(user_email)
        if "@dapperlabs.com" in user_email:
            org = 'dapper'
            portfolio = 'portfolio@dapperlabs.com'
        elif "@axiomzen.co" in user_email:
            org = 'az'
            portfolio = 'portfolio@axiomzen.co'
        elif "zenhub.com" in user_email:
            org = 'zenhub'
            portfolio = 'portfolio@zenhub.com'
        # Create Account
        add_to_g(user_email, user_first, user_last, personal_email, org)
        # Add to AZ GH
        add_to_gh_org('memberships', 'axiomzen', user_gh)

        # Add to portfolio@
        add_to_ggroup(user_email, 'axiomzen', 'portfolio@axiomzen.co')
        add_to_ggroup(user_email, 'dapper', 'portfolio@dapperlabs.com')
        add_to_ggroup(user_email, 'zenhub', 'portfolio@zenhub.com')
        
        # Dapper Steps
        if "@dapperlabs.com" in user_email:
            # Add to all-dapper@az
            add_to_ggroup(user_email, 'axiomzen', 'dapper-team@axiomzen.co')
            # Add to all-dapper@zenhub
            add_to_ggroup(user_email, 'zenhub', 'dapper-team@zenhub.com')
            # Add to team@dapper
            add_to_ggroup(user_email, 'dapper', 'team@dapperlabs.com')
            # Add to DapperLabs GH
            add_to_gh_org('memberships', 'dapperlabs', user_gh)
            # Add to Launchpad in AZ GH
            add_to_gh_team('teams', 'axiomzen', user_gh, '2702584')
        # AxiomZen Steps
        elif "@axiomzen.co" in user_email:
            # Add to all-az@dapper
            add_to_ggroup(user_email, 'dapper', 'all-az@axiomzen.co')
            # Add to all-az@zenhub
            add_to_ggroup(user_email, 'zenhub', 'all-az@axiomzen.co')
            # Add to All Axiomz in AZ GH
            add_to_gh_team('teams', 'axiomzen', user_gh, '2672396')
        # ZenHub Steps
        elif "@zenhub.com" in user_email:
            # Add to -team@az
            add_to_ggroup(user_email, 'axiomzen', 'zenhub-team@axiomzen.co')
            # Add to team@zenhub
            add_to_ggroup(user_email, 'zenhub', 'team@zenhub.com')
            # Add to -team@dapper
            add_to_ggroup(user_email, 'dapper', 'zenhub-team@dapperlabs.com')
            # Add to all@zenhub
            add_to_ggroup(user_email, 'zenhub', 'all@zenhub.com')
            # Add to Launchpad in AZ GH
            add_to_gh_team('teams', 'axiomzen', user_gh, '2702584')
            # Add to ZH GH
            add_to_gh_org('memberships', 'ZenHubHQ', user_gh)
        
        # Add Global Calendar
        add_to_gcal(user_email, 'axiomzen', 
            'axiomzen.co_7le38v8g471ki5a03mpl53r12c@group.calendar.google.com')
        # Add Social Calendar
        add_to_gcal(user_email, 'axiomzen', 
            'axiomzen.co_qfek8l7cbmef21cktl64djmq88@group.calendar.google.com')
        # Add portfolio to calendar
        add_to_gcal(portfolio, org, user_email)
