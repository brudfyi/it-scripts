
import requests
import os

# get api key from environment
api_key = os.getenv('OKTA_API_KEY')

# fail for bad api keys
if api_key == None or api_key == '':
    raise "OKTA_API_KEY environment variable is missing"

headers = {
    'Authorization': f'SSWS {api_key}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


def get_paginated_results(url, page_size=200):
    # create a result list within the function and return it at the end
    result = []
    # create the first url without pagination
    next_url = f'{url}?limit={page_size}'

    while next_url is not None:
        response = requests.get(next_url, headers=headers)
        response.raise_for_status()
        result += response.json()

        # if the current page doesn't have a next link, set next_url to exit condition
        if 'next' in response.links:
            next_url = response.links['next']['url']
        else:
            next_url = None

    # return the result after all pages were pulled
    return result


if __name__ == "__main__":
    groups_url = 'https://axiomzenportfolio.okta.com/api/v1/groups'
    users_url = 'https://axiomzenportfolio.okta.com/api/v1/users'
    apps_url = 'https://axiomzenportfolio.okta.com/api/v1/apps'

    print(get_paginated_results(groups_url))
    print(get_paginated_results(users_url))
    print(get_paginated_results(apps_url))
