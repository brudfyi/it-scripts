##### Basic off board script
# 1. Changes username to first.last-archived
# 2. Removes all 
# 3. Archives user
# 4. Remove user from all groups
# 5. Transfers Drive files to manager
# 6. Create G Group with old username
# 7. Adds manager to Group


import subprocess
import sys


username = 'chris.knaggs'
org = 'dapper'
domain = 'dapperlabs.com'
manager = 'michael.gardner'
gam_command = '/home/michael_gardner/bin/gamadv-xtd3/gam'

# 1
try:
    print('Setting username to first.last-archived@')
    subprocess.run([gam_command,'select', org, 'update', 'user', username+'@'+domain, 'email', username+'-archived@'+domain], check = True)
except subprocess.CalledProcessError:
    print('SOMETHING WENT WRONG - Check username')
    sys.exit()

#2
try:
    print('Deleting all aliases')
    subprocess.run([gam_command,'select', org, 'user', username+'-archived', 'delete', 'aliases'], check = True)
except subprocess.CalledProcessError:
    print('SOMETHING WENT WRONG - Check aliases')
    sys.exit()

#3
try:
    print('Archiving user')
    subprocess.run([gam_command,'select',org,'update','user',username+'-archived','archived', 'on'], check = True)
except subprocess.CalledProcessError:
    print('SOMETHING WENT WRONG - Check Account Status')
    sys.exit()

#4
try:
    print('Removing Groups from user')
    subprocess.run([gam_command, 'select', org, 'user', username+'-archived', 'delete', 'groups'], check = True)
except subprocess.CalledProcessError:
    print('SOMETHING WENT WRONG - Check Group Assignments')
    sys.exit()

#5
try:
    print('Transferring drive files to manager')
    subprocess.run([gam_command, 'select', org, 'create', 'datatransfer',username+'-archived', 'gdrive', manager, 'privacy_level', 'shared,private'], check = True)
except subprocess.CalledProcessError:
    print('SOMETHING WENT WRONG - Check Drive Migration')
    sys.exit()

#6
try:
    print('Creating G-Group with old user email')
    subprocess.run([gam_command, 'select', org, 'create', 'group', username+'@'+domain], check = True)
except subprocess.CalledProcessError:
    print('SOMETHING WENT WRONG - Check New Group')
    sys.exit()

#7
try:
    print('Add manager to G-Group')
    subprocess.run([gam_command,'select', org, 'update', 'group', username+'@'+domain,'add', manager+'@'+domain], check = True)
except subprocess.CalledProcessError:
    print('SOMETHING WENT WRONG - Check Group Membership')
    sys.exit()


