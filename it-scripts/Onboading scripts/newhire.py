
#Script that take users email and assigns them to the correct google groups based on their org


import os

user = 'chris.knaggs@dapperlabs.com'
gam_command = '/home/michael_gardner/bin/gamadv-xtd3/gam'

#Function to set org
def add_user_to_groups(email):
    if 'dapperlabs.com' in email:
        org = 'dapper'
        return org
    elif 'axiomzen.co' in email and '.com' not in email:
        org = 'az'
        return org
    elif 'zenhub.com' in email:
        org = 'zenhub'
        return org
    else:
        print('Invalid email')


if add_user_to_groups(user) == 'az':
    try:
        print()
        print('-------- Allows people to view Calendar --------')
        os.system(gam_command+' select az calendar ' +user+ ' add acls reader wholeportfolio@axiomzen.co sendnotifications false')
    except Exception:
        pass
    try:
        print()
        print('-------- Adding user to axiomzen-team@dapperlabs.com --------')
        os.system(gam_command+' select dapper update group axiomzen-team@dapperlabs.com add ' +user)
    except Exception:
        pass
    try:
        print()
        print('-------- Adding users to axiomzen-teamzenhub.com --------')
        os.system(gam_command+' select zenhub update group axiomzen-team@zenhub.com add ' +user)
    except Exception:
        pass
    try:
        print()
        print('-------- Adding users to wholeportfolio@axiomzen.co --------')
        os.system(gam_command+' select az update group wholeportfolio@axiomzen.co add '+user)
    except Exception:
        pass
    try:
        print()
        print('-------- Adding users to wholeportfolio@dapperlabs.com --------')
        os.system(gam_command+' select dapper update group wholeportfolio@dapperlabs.com add '+user)
    except Exception:
        pass
    try:
        print()
        print('-------- Adding users to wholeportfolio@zenhub.com --------')
        os.system(gam_command+' select zenhub update group wholeportfolio@zenhub.com add '+user)
    except Exception:
        pass

if add_user_to_groups(user) == 'dapper':
    try:
        print()
        print('-------- Allows people to view Calendar --------')
        os.system(gam_command+' select dapper calendar ' +user+ ' add acls reader wholeportfolio@dapperlabs.com sendnotifications false')
    except Exception:
        pass
    try:
        print()
        print('-------- Adding user to dapper-team@axiomzen.co --------')
        os.system(gam_command+' select az update group dapper-team@axiomzen.co add ' +user)
    except Exception:
        pass
    try:
        print()
        print('-------- Adding user to dapper-teamzenhub.com --------')
        os.system(gam_command+' select zenhub update group dapper-team@zenhub.com add ' +user)
    except Exception:
        pass
    try:
        print()
        print('-------- Adding user to wholeportfolio@axiomzen.co --------')
        os.system(gam_command+' select az update group wholeportfolio@axiomzen.co add '+user)
    except Exception:
        pass
    try:
        print()
        print('-------- Adding user to wholeportfolio@dapperlabs.com --------')
        os.system(gam_command+' select dapper update group wholeportfolio@dapperlabs.com add '+user)
    except Exception:
        pass
    try:
        print()
        print('-------- Adding user to wholeportfolio@zenhub.com --------')
        os.system(gam_command+' select zenhub update group wholeportfolio@zenhub.com add '+user)
    except Exception:
        pass



if add_user_to_groups(user) == 'zenhub':
    try:
        print()
        print('-------- Allows people to view Calendar --------')
        os.system(gam_command+' select zenhub calendar ' +user+ ' add acls reader wholeportfolio@zenhub.com sendnotifications false')
    except Exception:
        pass
    try:
        print()
        print('-------- Adds user to zenhub-team@axiomzen.co --------')
        os.system(gam_command+' select az update group zenhub-team@axiomzen.co add ' +user)
    except Exception:
        pass
    try:
        print()
        print('-------- Adds users to zenhub-team@dapperlabs.com --------')
        os.system(gam_command+' select zenhub update group zenhub-team@dapperlabs.com add ' +user)
    except Exception:
        pass
    try:
        print()
        print('-------- Adds users to wholeportfolio@axiomzen.co --------')
        os.system(gam_command+' select az update group wholeportfolio@axiomzen.co add '+user)
    except Exception:
        pass
    try:
        print()
        print('-------- Adds users to portfolio@dapperlabs.com --------')
        os.system(gam_command+' select dapper update group wholeportfolio@dapperlabs.com add '+user)
    except Exception:
        pass
    try:
        print()
        print('-------- Adds users to portfolio@zenhub.com --------')
        os.system(gam_command+' select zenhub update group wholeportfolio@zenhub.com add '+user)
    except Exception:
        pass    
