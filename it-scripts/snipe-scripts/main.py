import json
import requests
import time
import os
import re
import math
import string

# Set default variables
snipe_api_count = 0
first_snipe_call = None
rateLimited = True
verifySSL = True
forceUpdate = False
created_users = 0
created_manufacturers = 0
created_computers = 0
created_models = 0
created_peripherals = 0

def snipe_pubsub(event, context):

    global snipemanufacturers
    global snipeusers
    global snipemodels
    global snipelicenses
    global modelnumbers
    
    #  A list of valid subsets in a JAMF response
    validsubset = [
        "general",
        "location",
        "purchasing",
        "peripherals",
        "hardware",
        "certificates",
        "software",
        "extension_attributes",
        "groups_accounts",
        "iphones",
        "configuration_profiles"
    ]

    # Get the environment variables
    jamfpro_base = os.environ.get('JAMF_URL', False)
    jamf_api_user = os.environ.get('JAMF_USERNAME', False)
    jamf_api_password = os.environ.get('JAMF_PASSWORD', False)
    okta_base = os.environ.get('OKTA_URL', False)
    okta_api_key = os.environ.get('OKTA_API_KEY', False)
    okta_filter = os.environ.get('OKTA_FILTER', '')
    snipe_base = os.environ.get('SNIPE_URL', False)
    snipe_api_key = os.environ.get('SNIPE_API_KEY', False)
    defaultStatus = os.environ.get('SNIPE_DEF_STATUS', 2)
    emailDomain = os.environ.get('EMAIL_DOMAIN', False)
    snipe_computer_id = os.environ.get('SNIPE_COMP_ID', False)
    snipe_mobile_id = os.environ.get('SNIPE_MOBILE_ID', False)
    snipe_peripheral_id = os.environ.get('SNIPE_PERIPH_ID', False)
    snipe_computer_fields_id = os.environ.get('SNIPE_COMP_FIELDS_ID', False)
    snipe_mobile_fields_id = os.environ.get('SNIPE_MOBILE_FIELDS_ID', False)
    import_limit = os.environ.get('IMPORT_LIMIT', 0)
    amazon_ca_id = os.environ.get('AMAZON_CA_ID', False)
    amazon_us_id = os.environ.get('AMAZON_US_ID', False)

    import_limit = int(import_limit)

    # Check settings
    if not jamfpro_base:
        raise SystemExit("Please set the JAMF_URL environmental variable.")
    if not jamf_api_user:
        raise SystemExit("Please set the JAMF_USERNAME environmental variable.")
    if not jamf_api_password:
        raise SystemExit("Please set the JAMF_PASSWORD environmental variable.")
    if not okta_base:
        raise SystemExit("Please set the OKTA_URL environmental variable.")
    if not snipe_base:
        raise SystemExit("Please set the SNIPE_URL environmental variable.")
    if not snipe_api_key:
        raise SystemExit("Please set the SNIPE_API_KEY environmental variable.")
    if not okta_api_key:
        raise SystemExit("Please set the OKTA_API_KEY environmental variable.")
    if not emailDomain:
        raise SystemExit("Please set the EMAIL_DOMAIN environmental variable.")
    if not snipe_computer_id:
        raise SystemExit("Please set the SNIPE_COMP_ID environmental variable.")
    if not snipe_mobile_id:
        raise SystemExit("Please set the SNIPE_MOBILE_ID environmental variable.")
    if not snipe_peripheral_id:
        raise SystemExit("Please set the SNIPE_PERIPH_ID environmental variable.")

    # Set API headers
    jamfheaders = {'Accept': 'application/json'}
    snipeheaders = {'Authorization': 'Bearer {}'.format(snipe_api_key), 'Accept': 'application/json','Content-Type':'application/json'}
    oktaheaders = {'Authorization': 'SSWS {}'.format(okta_api_key), 'Accept': 'application/json', 'Content-Type':'application/json'}

    # Utility functions
    def request_handler(r, *args, **kwargs):
        global snipe_api_count
        global first_snipe_call
        if (snipe_base in r.url) and rateLimited:
            if '"messages":429' in r.text:
                time.sleep(2)
                re_req = r.request
                s = requests.Session()
                return s.send(re_req)
            if snipe_api_count == 0:
                first_snipe_call = time.time()
                time.sleep(0.5)
            snipe_api_count += 1
            time_elapsed = (time.time() - first_snipe_call)
            snipe_api_rate = snipe_api_count / time_elapsed
            if snipe_api_rate > 1.95:
                sleep_time = 0.5 + (snipe_api_rate - 1.95)
                #print("Going over snipe rate limit of 120/minute ({}/minute), sleeping for {}".format(snipe_api_rate,sleep_time))
                time.sleep(sleep_time)
        if '"messages":429' in r.text:
            print(r.content)
            raise SystemExit("Rate limiting has been enforced")
        return r

    # JAMF functions

    # Get a list of all JAMF computers
    def get_jamf_computers():
        api_url = "{}/JSSResource/computers".format(jamfpro_base)
        response = requests.get(api_url, auth=(jamf_api_user, jamf_api_password), headers=jamfheaders, verify=verifySSL, hooks={'response': request_handler})
        if response.status_code == 200:
            return response.json()
        elif b'policies.ratelimit.QuotaViolation' in response.content:
            print("JAMF responded with error code: {} - Policy Ratelimit Quota Violation. Waiting to retry the lookup.".format(response))
            time.sleep(75)
            print("Finished waiting. Retrying lookup...")
            newresponse = get_jamf_computers()
            return newresponse
        else:
            print("Received an invalid status code when trying to retreive JAMF computer list: {} - {}".format(response.status_code, response.content))
            return None

    # Get a list of all JAMF computers
    def get_jamf_mobiles():
        api_url = "{}/JSSResource/mobiledevices".format(jamfpro_base)
        response = requests.get(api_url, auth=(jamf_api_user, jamf_api_password), headers=jamfheaders, verify=verifySSL, hooks={'response': request_handler})
        if response.status_code == 200:
            return response.json()
        elif b'policies.ratelimit.QuotaViolation' in response.content:
            print("JAMF responded with error code: {} - Policy Ratelimit Quota Violation. Waiting to retry the lookup.".format(response))
            time.sleep(75)
            print("Finished waiting. Retrying lookup...")
            newresponse = get_jamf_mobiles()
            return newresponse
        else:
            print("Received an invalid status code when trying to retreive JAMF mobile list: {} - {}".format(response.status_code, response.content))
            return None

    # Search for JAMF asset by id
    def search_jamf_asset(jamf_id, computer=True):
        if computer:
            api_url = "{}/JSSResource/computers/id/{}".format(jamfpro_base, jamf_id)
        else:
            api_url = "{}/JSSResource/mobiledevices/id/{}".format(jamfpro_base, jamf_id)
        response = requests.get(api_url, auth=(jamf_api_user, jamf_api_password), headers=jamfheaders, verify=verifySSL, hooks={'response': request_handler})
        if response.status_code == 200:
            jsonresponse = response.json()
            if computer and 'computer' in jsonresponse:
                return jsonresponse['computer']
            elif not computer and 'mobile_device' in jsonresponse:
                return jsonresponse['mobile_device']
            else:
                return False
        elif b'policies.ratelimit.QuotaViolation' in response.content:
            print("JAMF responded with error code: {} - Policy Ratelimit Quota Violation. Waiting to retry the lookup.".format(response))
            time.sleep(75)
            print("Finished waiting. Retrying lookup...")
            newresponse = search_jamf_asset(jamf_id, computer)
            return newresponse
        else:
            print("JAMF responded with error code: {} when searching for asset id: {}".format(response, jamf_id))
            return None

    # Function to lookup a snipe asset by serial number.
    def search_snipe_asset(serial):
        api_url = '{}/api/v1/hardware/byserial/{}'.format(snipe_base, serial)
        response = requests.get(api_url, headers=snipeheaders, verify=verifySSL, hooks={'response': request_handler})
        if response.status_code == 200:
            jsonresponse = response.json()
            # Check to make sure there's actually a result
            if jsonresponse['total'] == 1:
                return jsonresponse
            elif jsonresponse['total'] == 0:
                return "NoMatch"
            else:
                return "MultiMatch"
        else:
            print("Snipe-IT responded with error code: {} when we tried to look up: {}".format(response.text, serial))
            return "ERROR"

    # Function to get all item of a certain type (models/licenses)
    def get_snipe_list(list_type):
        api_url = '{}/api/v1/{}'.format(snipe_base, list_type)
        response = requests.get(api_url, headers=snipeheaders, verify=verifySSL, hooks={'response': request_handler})
        if response.status_code == 200:
            jsonresponse = response.json()
            if jsonresponse['total'] <= len(jsonresponse['rows']) :
                return jsonresponse
            else:
                api_url = '{}/api/v1/{}?limit={}'.format(snipe_base, list_type, jsonresponse['total'])
                newresponse = requests.get(api_url, headers=snipeheaders, verify=verifySSL, hooks={'response': request_handler})
                if newresponse.status_code == 200:
                        newjsonresponse = newresponse.json()
                        if newjsonresponse['total'] == len(newjsonresponse['rows']) :
                            return newjsonresponse
                        else:
                            raise SystemExit("Unable to get all {} objects from the Snipe-IT instanace".format(list_type))
                else:
                        raise SystemExit("Attempted to retreive a list of {}, Snipe-IT responded with error status code:{} - {}".format(list_type, response.status_code, response.content))
        else:
            raise SystemExit("Attempted to retreive a list of {}, Snipe-IT responded with error status code:{} - {}".format(list_type, response.status_code, response.content))


    # Recursive function returns all users in a Snipe Instance, 100 at a time.
    def get_snipe_users(previous=[]):
        user_id_url = '{}/api/v1/users'.format(snipe_base)
        payload = {
            'limit': 100,
            'offset': len(previous)
        }
        response = requests.get(user_id_url, headers=snipeheaders, json=payload, hooks={'response': request_handler})
        response_json = response.json()
        current = response_json['rows']
        if len(previous) != 0:
            current = previous + current
        if response_json['total'] > len(current):
            return get_snipe_users(current)
        else:
            return current

    # Function to search snipe for a user
    def get_snipe_user_id(name):
        if name == '' or not name:
            return False
        name = name.lower()
        is_username = ' ' not in name
        for user in snipeusers:
            if (is_username and user['username'].lower() == name) or (not is_username and user['name'].lower() == name):
                return user['id']
        return False

    def get_snipe_username(id):
        for user in snipeusers:
            if user['id'] == id:
                return user['username']
        return False

    # Function that creates a new Snipe Model - not an asset - with a JSON payload
    def create_snipe_model(payload):
        global modelnumbers
        global created_models

        api_url = '{}/api/v1/models'.format(snipe_base)
        response = requests.post(api_url, headers=snipeheaders, json=payload, verify=verifySSL, hooks={'response': request_handler})
        if response.status_code == 200:
            jsonresponse = response.json()
            modelnumbers[jsonresponse['payload']['model_number']] = jsonresponse['payload']['id']
            created_models = created_models + 1
            return True
        else:
            print("Error code: {} while trying to create a new Snipe-IT model.".format(response.status_code))
            return False

    # Function to create a new asset by passing array
    def create_snipe_asset(payload):
        api_url = '{}/api/v1/hardware'.format(snipe_base)
        response = requests.post(api_url, headers=snipeheaders, json=payload, verify=verifySSL, hooks={'response': request_handler})
        if response.status_code == 200:
            return 'AssetCreated', response
        else:
            print("Snipe-IT asset creation failed for asset {} with error {}".format(payload['name'],response.text))
            return response

    # Function that updates a snipe asset with a JSON payload
    def update_snipe_asset(snipe_id, payload):
        api_url = '{}/api/v1/hardware/{}'.format(snipe_base, snipe_id)
        response = requests.patch(api_url, headers=snipeheaders, json=payload, verify=verifySSL, hooks={'response': request_handler})
        # Verify that the payload updated properly.
        goodupdate = True
        if response.status_code == 200:
            jsonresponse = response.json()
            for key in payload:
                if key == 'purchase_date':
                        payload[key] = payload[key] + " 00:00:00"
                if payload[key] == '':
                        payload[key] = None
                if jsonresponse['payload'][key] != payload[key]:
                        print("Unable to update ID: {}. Failed to update the {} field with '{}'".format(snipe_id, key, payload[key]))
                        goodupdate = False
            return goodupdate
        else:
            print("Got error status code while updating ID {}: {} - {}".format(snipe_id, response.status_code, response.content))
            return False

    # Function that checks in an asset in snipe
    def checkin_snipe_asset(asset_id):
        api_url = '{}/api/v1/hardware/{}/checkin'.format(snipe_base, asset_id)
        payload = {
            'note':'Checked in automatically.'
        }
        response = requests.post(api_url, headers=snipeheaders, json=payload, verify=verifySSL, hooks={'response': request_handler})
        if response.status_code == 200:
            return "CheckedOut"
        else:
            return response

    # Function that checks out an asset in snipe
    def checkout_snipe_asset(user_id, asset_id, checked_out_user=None):
        if not user_id:
            return "NotFound"
            print("First time this asset will be checked out, checking out to user id {}".format(user_id))
        elif type(checked_out_user) is dict:
            if checked_out_user['id'] == user_id:
                return 'CheckedOut'
            else:
                checkin_snipe_asset(asset_id)
            
        api_url = '{}/api/v1/hardware/{}/checkout'.format(snipe_base, asset_id)
        payload = {
            'checkout_to_type': 'user',
            'assigned_user': user_id,
            'note': 'Checked out automatically'
        }
        response = requests.post(api_url, headers=snipeheaders, json=payload, verify=verifySSL, hooks={'response': request_handler})
        if response.status_code == 200:
            return "CheckedOut"
        else:
            print("Asset checkout failed for asset {} with error {}".format(asset_id, response.text))
            return response

    # Function to strip punctuation from a string
    def strip_punct(s):
        return s.translate(str.maketrans('', '', string.punctuation))

    # Function to create a manufacturer in Snipe
    def create_snipe_manufacturer(name):
        global snipemanufacturers
        global created_manufacturers
        api_url = '{}/api/v1/manufacturers'.format(snipe_base)
        payload = {
            'name': name
        }
        response = requests.post(api_url, headers=snipeheaders, json=payload, verify=verifySSL, hooks={'response': request_handler})
        if response.status_code == 200:
            print("Created manufacturer '{}'.".format(name)) 
            jsonresponse = response.json()
            if 'payload' in jsonresponse and 'id' in jsonresponse['payload']:
                snipemanufacturers['rows'].append(jsonresponse['payload'])
                created_manufacturers = created_manufacturers + 1
                return jsonresponse['payload']['id']
            else:
                return False
        else:
            print("Error code: {} while trying to create a new manufacturer.".format(response.status_code))
            return False

    # Function to get a manufacturer id in Snipe
    def get_snipe_manufacturer_id(name):
        for manufacturer in snipemanufacturers['rows']:
            if manufacturer['name'].lower() == name.lower():
                return manufacturer['id']
        return False

    def get_okta_groups(group_name=False):
        url = "{}/api/v1/groups".format(okta_base)
        response = requests.get(url, headers=oktaheaders, hooks={'response': request_handler})
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
            response = requests.get(url, headers=oktaheaders, hooks={'response': request_handler})
            if response.status_code == 200:
                current = response.json()
                return current
            else:
                print("Okta users for group request failed with error {}".format(response.text))
                return False
        else:
            print("Could not retrieve Okta group with the name {}".format(group_name))
            return False



    def get_okta_group(group_name):
        url = "{}/api/v1/groups?q={}".format(okta_base, group_name)
        response = requests.get(url, headers=oktaheaders, hooks={'response': request_handler})
        if response.status_code == 200:
            current = response.json()
        else:
            print("Okta user group request failed with error {}".format(response.text))
            return False

     # Function to retrieve all (active) users from Okta
    def get_okta_users(previous=[], limit=200):
        after = ''
        if len(previous) != 0:
            after = '&after={}'.format(previous[-1]['id'])
        url = "{}/api/v1/users?filter=status%20eq%20%22ACTIVE%22{}&limit={}".format(okta_base, after, limit)
        response = requests.get(url, headers=oktaheaders, hooks={'response': request_handler})
        if response.status_code == 200:
            current = response.json()
            count = len(current)
            if len(previous) != 0:
                current = previous + current
            if count == limit and len(current) < 1000:
                return get_okta_users(current, limit)
            else:
                return current
        else:
            print("Okta user list request failed with error {}".format(response.text))
            return previous

    # Function to create a Snipe user
    def create_snipe_user(payload):
          global snipeusers
          global created_users
          api_url = '{}/api/v1/users'.format(snipe_base)
          response = requests.post(api_url, headers=snipeheaders, json=payload, verify=verifySSL, hooks={'response': request_handler})
          if response.status_code == 200:
               jsonresponse = response.json()
               if 'payload' in jsonresponse and jsonresponse['payload'] is not None:
                    user_obj = {'id': jsonresponse['payload']['id'], 'username': jsonresponse['payload']['username'], 'name': jsonresponse['payload']['name'], 'last_updated': 0}
                    snipeusers.append(user_obj)
                    created_users = created_users + 1
                    return True
               else:
                    print("Missing payload for Snipe-IT user creation.")
                    return False
          else:
               print("User creation failed for {} with error {}".format(payload['username'],response.text))
               return False

    # Get all the Snipe-IT bits and bobs
    snipemodels = get_snipe_list('models')
    snipelicenses = get_snipe_list('licenses')
    snipemanufacturers = get_snipe_list('manufacturers')
    snipeusers = get_snipe_users()
    snipefields = get_snipe_list('fields')

    # Make snipeusers more manageable
    tmp_users = []
    for user in snipeusers:
        user_obj = {'id': user['id'], 'username': user['username'], 'name': user['name'], 'last_updated': 0}
        if 'updated_at' in user and user['updated_at'] is not None:
            user_obj['last_updated'] = user['updated_at']['datetime']
        tmp_users.append(user_obj)
    snipeusers = tmp_users
    snipe_user_count = len(snipeusers)

    # Process the custom fields
    fields = {}
    for field in snipefields['rows']:
        if field['name'].lower() == 'mac address' or field['name'].lower() == 'mac':
            fields['mac'] = field['db_column_name']
        elif field['name'].lower() == 'cpu' or field['name'].lower() == 'processor':
            fields['cpu'] = field['db_column_name']
        elif 'imei' in field['name'].lower():
            fields['imei'] = field['db_column_name']
        elif 'year' in field['name'].lower():
            fields['year'] = field['db_column_name']
        elif 'ram' in field['name'].lower() or field['name'].lower() == 'memory':
            fields['ram'] = field['db_column_name']
        elif field['name'].lower() == 'filevault enabled':
            fields['filevault_enabled'] = field['db_column_name']
        elif field['name'].lower() == 'os' or field['name'].lower() == 'operating system':
            fields['os'] = field['db_column_name']
        elif field['name'].lower() == 'storage' or field['name'].lower() == 'hd':
            fields['storage'] = field['db_column_name']

    modelnumbers = {}
    peripherals = {}
    for model in snipemodels['rows']:
        if model['model_number'] == "":
            continue
        elif model['category']['id'] == int(snipe_peripheral_id):
            peripherals[model['id']] = model['name']
        modelnumbers[model['model_number']] = model['id']

    # Get Okta users
    okta_users = get_okta_users()
    dc_users = get_okta_users_for_group('Dapper Collectives')
    dc_user_ids = []
    dc_id = 1
    okta_user_count = len(okta_users)
    if dc_users:
        for dc_user in dc_users:
            dc_user_ids.append(dc_user['profile']['login'])


    # Try to avoid script timeout in cloud by separating large operations, adding a large amount of users might take up too much time...

    print("Updating Snipe-IT users..")

    if okta_filter != '':
        print("A total of {} Okta users were retrieved fron the Okta API, which will be filtered based on user the department containing '{}'.".format(okta_user_count, okta_filter.lower()))
    else:
        print("A total of {} Okta users were retrieved fron the Okta API".format(len(okta_users)))
    for okta_user in okta_users:
        if import_limit == 0 or snipe_user_count < import_limit:
            if not get_snipe_user_id(okta_user['profile']['login']) and 'department' in okta_user['profile'] and okta_user['profile']['department'] is not None and okta_filter in okta_user['profile']['department'].lower() and '.team' not in okta_user['profile']['email']:
                # Even though login will be disabled for the user, we have to set a password (otherwise the user will not be created)
                pw = '0@8OD3+3Q>eDD^Y'
                payload = {'first_name': okta_user['profile']['firstName'], 'last_name': okta_user['profile']['lastName'], 'username': okta_user['profile']['login'], 'password': pw, 'password_confirmation': pw}
                if 'title' in okta_user['profile'] and okta_user['profile']['title'] is not None:
                    payload['jobtitle'] = okta_user['profile']['title']
                create_snipe_user(payload)
                snipe_user_count = snipe_user_count + 1
    okta_users = None

    if created_users <= 20:

        CurrentNumber = 0

        # Get JAMF the IDS of all active assets
        jamf_computer_list = get_jamf_computers()
        jamf_mobile_list = get_jamf_mobiles()
        print("A total of {} computers were retrieved fron the JAMF API".format(len(jamf_computer_list['computers'])))

        jamf_types = {
            'computers': jamf_computer_list,
            'mobile_devices': jamf_mobile_list
        }

        # Get Google devices
        google_device_list = []

        # Off we go!!!!
        if import_limit == 0:
            print("Updating Snipe-IT assets..")
        else:
            print("Processing Snipe-IT assets (limited to {})...".format(import_limit))

        CurrentNumber = 0
        MobileCount = 0
        ComputerCount = 0

        for jamf_type in jamf_types:

            for jamf_asset in jamf_types[jamf_type][jamf_type]:

                if import_limit == 0 or CurrentNumber < import_limit:

                    CurrentNumber += 1

                    if jamf_type == 'mobile_devices':
                        MobileCount += 1
                    else:
                        ComputerCount += 1


                    # Search through the list by ID for all asset information\
                    if jamf_type == 'computers':
                        jamf = search_jamf_asset(jamf_asset['id'])
                    else:
                        jamf = search_jamf_asset(jamf_asset['id'], False)

                    if jamf is None:
                        continue

                    # Check that the manufacturer exists, if not create it.
                    make = 'Apple'
                    man_id = get_snipe_manufacturer_id(make)
                    if not man_id:
                        man_id = create_snipe_manufacturer(make)

                    # Who is the device checked out to?
                    username = False
                    user_id = False
                    user = 'Unknown'

                    # What is the name of the person?
                    if 'location' in jamf and 'username' in jamf['location'] and jamf['location']['username'] is not None and jamf['location']['username'] != '':
                        username = jamf['location']['username']
                        if '@' not in username:
                            username = '{}@{}'.format(username, emailDomain)
                        user_id = get_snipe_user_id(username)
                        user = jamf['location']['real_name']
                        if user == '':
                            user == jamf['location']['realname']
                            if user == '':
                                user = 'Unknown'
                    elif jamf_type == 'computers' and 'groups_accounts' in jamf and 'local_accounts' in jamf['groups_accounts'] and jamf['groups_accounts']['local_accounts'] is not None:
                        for user_account in jamf['groups_accounts']['local_accounts']:
                            if ' ' in user_account['realname']:
                                user = user_account['realname']
                                user_id = get_snipe_user_id(user)
                                username = get_snipe_username(user_id)
                                if user_id:
                                    break


                    if user_id and username and username in dc_users:
                        dc_user = True
                    else:
                        dc_user = False



                else:

                    user_id = False
                    dc_user = False


                # Do we have a manufacturer id so that we can proceed?
                if man_id:

                    # Check that the model number exists in snipe, if not create it.
                    if jamf_type == 'computers':
                        if jamf['hardware']['model_identifier'] not in modelnumbers:
                            # logging.info("Could not find a model ID in snipe for: {}".format(jamf['hardware']['model_identifier']))
                            newmodel = {"category_id": int(snipe_computer_id), "manufacturer_id": man_id, "name": jamf['hardware']['model'], "model_number": jamf['hardware']['model_identifier']}
                            if snipe_computer_fields_id:
                                newmodel['fieldset_id'] = int(snipe_computer_fields_id)
                            create_snipe_model(newmodel)
                    elif jamf_type == 'mobile_devices':
                        if jamf['general']['model_identifier'] not in modelnumbers:
                            # logging.info("Could not find a model ID in snipe for: {}".format(jamf['general']['model_identifier']))
                            newmodel = {"category_id": int(snipe_mobile_fields_id), "manufacturer_id": man_id, "name": jamf['general']['model'], "model_number": jamf['general']['model_identifier']}
                            if snipe_mobile_fields_id:
                                newmodel['fieldset_id'] = int(snipe_mobile_fields_id)
                            create_snipe_model(newmodel)

                    # Pass the SN from JAMF to search for a match in Snipe
                    snipe = search_snipe_asset(jamf['general']['serial_number'])

                    # Create a new asset if there's no match:
                    if snipe == 'NoMatch':

                        #logging.info("Creating a new asset in snipe for JAMF ID {} - {}".format(jamf['general']['id'], jamf['general']['name']))
                        # This section checks to see if the asset tag was already put into JAMF, if not it creates one with with Jamf's ID.
                        t = '{}'.format(jamf['general']['id'])
                        if jamf_type == 'mobile_devices':
                            jamf_asset_tag = 'jamfid-m-{}'.format(t.zfill(3))
                        else:
                            jamf_asset_tag = 'jamfid-{}'.format(t.zfill(3))

                        # Create the payload
                        if jamf_type == 'mobile_devices':
                            #logging.debug("Payload is being made for a mobile device")
                            newasset = {'asset_tag': jamf_asset_tag, 'model_id': modelnumbers['{}'.format(jamf['general']['model_identifier'])], 'name': strip_punct(jamf['general']['name']), 'status_id': defaultStatus, 'serial': jamf['general']['serial_number']}
                            # add custom field data...
                            #if snipe_mobile_fields_id:
                            #    if 'mac' in fields:
                            #        newasset[fields['mac']] = jamf['general']['mac_address']
                            #    if 'imei' in fields:
                            #        newasset[fields['imei']] = jamf['general']['mac_address']
                            #    if 'os' in fields:
                            #        newasset[fields['os']] = '{} {}'.format(jamf['hardware']['os_name'], jamf['hardware']['os_version'])
                        elif jamf_type == 'computers':
                            #logging.debug("Payload is being made for a computer")
                            newasset = {'asset_tag': jamf_asset_tag, 'model_id': modelnumbers['{}'.format(jamf['hardware']['model_identifier'])], 'name': strip_punct(jamf['general']['name']), 'status_id': defaultStatus, 'serial': jamf['general']['serial_number'], 'notes': 'Assigned to {}.'.format(user)}
                            # add custom field data...
                            if snipe_computer_fields_id:
                                if 'mac' in fields:
                                    newasset[fields['mac']] = jamf['general']['mac_address']
                                if 'cpu' in fields:
                                    newasset[fields['cpu']] = jamf['hardware']['processor_type']
                                if 'year' in fields:
                                    match = re.search('\d{4}', jamf['hardware']['model'])
                                    if match:
                                        newasset[fields['year']] = int(match.group(0))
                                if 'ram' in fields:
                                    newasset[fields['ram']] = '{} GB'.format(math.floor(int(jamf['hardware']['total_ram_mb']) / 1000))
                                if 'os' in fields:
                                    newasset[fields['os']] = '{} {}'.format(jamf['hardware']['os_name'], jamf['hardware']['os_version'])
                                if 'storage' in fields and 'storage' in jamf['hardware'] and len(jamf['hardware']['storage']) > 0:
                                    size = 25 * round(math.floor(int(jamf['hardware']['storage'][0]['size']) / 1000) / 25)
                                    unit = "GB"
                                    if size >= 1000:
                                        size = size / 1000
                                        unit = "TB"
                                    newasset[fields['storage']] = '{} {}'.format(size, unit)

                        if jamf['general']['serial_number'] == 'Not Available':
                            continue
                        else:
                            new_snipe_asset = create_snipe_asset(newasset)
                            if new_snipe_asset[0] != "AssetCreated":
                                continue
                            if user_id or forceUpdate:
                                checkout_snipe_asset(user_id, new_snipe_asset[1].json()['payload']['id'], "NewAsset")
                                if dc_user:
                                    update_snipe_asset(new_snipe_asset[1].json()['payload']['id'], {'company_id': dc_id})

                    # Log an error if there's an issue, or more than once match.
                    elif snipe == 'MultiMatch':
                        print("There are multiple assets with a serial number of {} in the inventory (may require purging deleted records in Snipe-IT settings).".format(jamf['general']['serial_number']))
                    elif snipe == 'ERROR':
                        print("Error looking up serial number {}.".format(jamf['general']['serial_number']))
                    else:
                        # Only update if JAMF has more recent info.
                        snipe_id = snipe['rows'][0]['id']
                        snipe_time = snipe['rows'][0]['updated_at']['datetime']
                        if jamf_type == 'computers':
                            jamf_time = jamf['general']['report_date']
                        elif jamf_type == 'mobile_devices':
                            jamf_time = jamf['general']['last_inventory_update']
                            
                        # Check to see that the JAMF record is newer than the previous Snipe update, or if it is a new record in Snipe
                        if jamf_time > snipe_time or forceUpdate:

                            mappings = {
                                'computers': [['name', 'general name']],
                                'mobile_devices': [['name', 'general name']]
                            }

                            for mapping in mappings[jamf_type]:
                                snipekey = mapping[0]
                                jamfsplit = mapping[1].split()
                                for i, item in enumerate(jamfsplit):
                                    if i == 0:
                                        jamf_value = jamf[item]
                                    else:
                                        if jamfsplit[0] == 'extension_attributes':
                                            for attribute in jamf_value:
                                                if attribute['id'] == item:
                                                    jamf_value = attribute['value']
                                        else:
                                            jamf_value = jamf_value[item]
                                payload = {
                                    snipekey: jamf_value
                                }
                                latestvalue = jamf_value

                                # Need to check that we're not needlessly updating the asset.
                                # If it's a custom value it'll fail the first section and send it to except section that will parse custom sections.
                                try:
                                    if snipe['rows'][0][snipekey] != latestvalue:
                                        update_snipe_asset(snipe_id, payload)
        
                                except:
                                    needsupdate = False
                                    for CustomField in snipe['rows'][0]['custom_fields']:
                                        if snipe['rows'][0]['custom_fields'][CustomField]['field'] == snipekey :
                                            if snipe['rows'][0]['custom_fields'][CustomField]['value'] != latestvalue:
                                                needsupdate = True
                                    if needsupdate is True:
                                        update_snipe_asset(snipe_id, payload)

                            # Device checkout
                            if (user_id and (snipe['rows'][0]['assigned_to'] == None or forceUpdate)):

                                if snipe['rows'][0]['status_label']['status_meta'] in ('deployable', 'deployed'):
                                    checkout_snipe_asset(user_id, snipe_id, snipe['rows'][0]['assigned_to'])
                                    if dc_user:
                                        update_snipe_asset(snipe_id, {'company_id': dc_id})

                                else:
                                    print("Unable to checkout {} because status is not set to deployable.".format(jamf['general']['name']))

        if created_users > 0:
            print("Created {} user account(s) in Snipe-IT.".format(created_users))
        if created_manufacturers > 0:
            print("Created {} manufacturer(s) in Snipe-IT.".format(created_manufacturers))
        if created_models > 0:
            print("Created {} model(s) in Snipe-IT.".format(created_models))
        if created_computers > 0:
            print("Created {} computers(s) in Snipe-IT.".format(created_computers))
    else:
        if created_users > 0:
            print("Created {} user account(s) in Snipe-IT.".format(created_users))
        print("Skipping updating Snipe-IT assets in this run.")
    print("Finished.")