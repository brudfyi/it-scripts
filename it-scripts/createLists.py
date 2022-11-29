# A script to add everyone to a certain set of groups based on their email
# 
# Args: <A csv with the cols:
#                      email > 
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

def adduser_group(email, group, org):
    try:
        subprocess.check_output([gam_command, 'select', org, 'update', 'group',
        group, 'add', 'member', 'user', email])
        print("- Adding {0} to {1}".format(email, group))
    except:
        print("- FAILED adding {0} to {1}".format(email, group))

print(user_data)

for index, row in user_data.iterrows():
    row = row.tolist()
    email = row[0]

    if "@dapperlabs.com" in email:
        # Portfolios
        adduser_group(email, 'portfolio@dapperlabs.com', 'dapper')
        adduser_group(email, 'portfolio@zenhub.com', 'zenhub')
        adduser_group(email, 'portfolio@axiomzen.co', 'az')
        
        # All dappers
        adduser_group(email, 'team@dapperlabs.com', 'dapper')
        adduser_group(email, 'dapper-team@zenhub.com', 'zenhub')
        adduser_group(email, 'dapper-team@axiomzen.co', 'az')
    if "@axiomzen.co" in email:
        # Portfolios
        adduser_group(email, 'portfolio@dapperlabs.com', 'dapper')
        adduser_group(email, 'portfolio@zenhub.com', 'zenhub')
        adduser_group(email, 'portfolio@axiomzen.co', 'az')
        # All AxiomZens
        adduser_group(email, 'team@axiomzen.co', 'az')
        adduser_group(email, 'axiomzen-team@zenhub.com', 'zenhub')
        adduser_group(email, 'axiomzen-team@dapperlabs.com', 'dapper')
    if "@zenhub.com" in email:
        # Portfolios
        adduser_group(email, 'portfolio@dapperlabs.com', 'dapper')
        adduser_group(email, 'portfolio@zenhub.com', 'zenhub')
        adduser_group(email, 'portfolio@axiomzen.co', 'az')
        # All ZenHub
        adduser_group(email, 'zenhub-team@dapperlabs.com', 'dapper')
        adduser_group(email, 'team@zenhub.com', 'zenhub')
        adduser_group(email, 'zenhub-team@axiomzen.co', 'az')
