# - This script sends everyone in an csv a slack message
#
# Args: <A csv with the cols:
#                      email, org >
#      slack-api-key
#
# TODO:
# - Move the message out of the script
import pandas
import argparse
import slack
import json

parser = argparse.ArgumentParser()
parser.add_argument("csv_user")
parser.add_argument("slack_key")
args = parser.parse_args()
colnames = ['email', 'org']
user_data = pandas.read_csv(args.csv_user, names=colnames)

sc = slack.WebClient(args.slack_key)

def message_user(email, message):
    try:
        user = sc.users_lookupByEmail(email=email)
        sc.chat_postMessage(as_user='true',
                channel=user['user']['id'],
                text=message)
        print("- Messaging {0}".format(email))
    except:
        print("- FAILED messaging {0}".format(email))

for index, row in user_data.iterrows():
    if index != 0:
        row = row.tolist()
        email = row[0]
        org = row[1]
        if org == 'd':
            subdomain = 'dapperlabs'
        elif org == 'z':
            subdomain = 'axiomlabs'
        elif org == 'a':
            subdomain = 'axiomzenportfolio'
        message = r"""Hey, sorry if you've already done this, if you think you have could you send me your Mac's serial number? If you haven't then could you pleeease enroll in Jamf or keep me in the loop with any issues you're having? :pray:
If you're not sure what Jamf is and would like more information, you can find an explanation here: https://docs.google.com/document/d/1rxxMjtKY1bpfBQAA9zRjz60s0ZttqVmux96j4z2uXVM/

There's a video below, but written instructions on how to install Jamf are here:
1) Open Safari
2) Go to: https://{subdomain}.jamfcloud.com/enroll
3) Login with the username/password: `{username}` / `{password}`
4) Leave `Assign to user` blank, just click Enroll
5) Press Continue to download the certificate
6) Install the certificate
7) Go back to Safari, click continue again to download the MDM profile
8) Install the MDM profile
9) Done!
*) At some point soon you'll be asked to enter your computer's password to get FileVault linked with Jamf.

There's a video here: https://drive.google.com/open?id=1yGkdbdxY_3XDwPYLy5oSz2GCm47c3JHq""".format(subdomain=subdomain,username=subdomain,password=subdomain)
        message_user(email, message)
