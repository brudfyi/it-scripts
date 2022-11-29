# A script to delete a csv list full of calendar events by event
# 
# example use: If a calendar migration copies too many events
# 
# Args: <A csv with the cols:
#                      email, calendar event id > 
# TODO:
# - 
import subprocess
import pandas
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("csv_user")
args = parser.parse_args()
user_data = pandas.read_csv(args.csv_user)

gam_command = ['python3', 
    '/Users/jessecrayston/Documents/gam/GAMADV-XTD3/src/gam.py']

def deleteevent_user(email, eventID, org):
    try:
        subprocess.check_output([gam_command, 'select', org, 'calendar', 
            email, 'deleteevent', 'eventid', eventID, 'doit'])
        print("- Deleting {0} from {1}".format(eventID, email))
    except:
        print("- FAILED deleting {0} from {1}".format(eventID, email))
print(user_data)

for index, row in user_data.iterrows():
        row = row.tolist()
        email = row[0]
        eventID = row[1]
        ## Note the org is explicityly stated here
        deleteevent_user(email, eventID, "dapper")
