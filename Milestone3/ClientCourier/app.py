
import json
from os import getenv
import requests
from dotenv import load_dotenv
from examples import custom_style_2 as custom_style
from jwt import ExpiredSignatureError, InvalidTokenError, decode, encode
from PyInquirer import Separator, prompt

load_dotenv()
JWT_SECRET = getenv("JWT_SECRET")


# Mile3: Web Service deployed on Heroku
API_URL = 'https://obscure-waters-56046.herokuapp.com/'

# Mile3: Local Web Service
# API_URL = 'http://127.0.0.1:5001'

courier_data = {}



'''=============== API Calls ==============='''


def show_labels( link ):
    
    links, embedded = api_call( 'GET', link )
    if embedded == 503:
        return 503
    labels = embedded['all_labels']
    table( headers=['Label ID', 'Owner'], data=labels )
    return labels


def show_packages( link ):
    
    links, embedded = api_call( 'GET', link )
    if embedded == 503:
        return 503
    packages = embedded['package_ids']
    table( headers=['Package ID', 'Courier'], data={
        p: courier_data['username'] for p in packages
    } )
    return packages
    

def create_package( link ):

    fetch_all_link = link.replace('<lid>', '')[:-1]
    labels = show_labels( fetch_all_link )
    if labels == 503:
        return 503

    questions = [ {
        'type': 'list',
        'name': 'which',
        'message': 'Which Label will be turned into Package?',
        'choices': list(labels.keys())
    }]

    answer = prompt(questions, style=custom_style)['which']
    # print(answer)


    link = link.replace('<lid>', answer)
    links, embedded = api_call( 'POST', link )
    if embedded == 503:
        return 503


def change_status( link ):
    
    fetch_all_link = link.split('<')[0][:-1]
    packages = show_packages( fetch_all_link )
    if packages == 503:
        return 503
    if not packages:
        print(f'No packages currently delivered by {courier_data["username"]}.\n')
        return

    questions = [ {
        'type': 'list',
        'name': 'pid',
        'message': 'Which Package status would you like to change?',
        'choices': list(packages)
    }, {
        'type': 'list',
        'name': 'status',
        'message': 'What status has it now?',
        'choices': [
            'Waiting for Courier',
            'Received by Courier',
            'Delivered'
        ]
    }
    ]

    answers = prompt(questions, style=custom_style)
    link = link.replace('<pid>', answers['pid'])
    link = link.replace('<status>', answers['status'])
    links, embedded = api_call( 'PUT', link )
    if embedded == 503:
        return 503



'''=============== Help Stuff ==============='''

def title( text ):
    print(f'\n============= {text} =============\n')


def table( headers, data ):

    separator = '\t\t'
    print('\n')
    for header in headers:
        print( f'{header}{separator}', end='' )
    print('\n')
    for lid, username in data.items():
        print( f'{lid}{separator}{username}', end='\n' )
    print('\n')

def issue_auth_token( username ):

    payload = {
        'iss': "ponczkomat auth server",
        'expiresIn': '24h',
        'usr': username,
        'aud': "ponczkomat tracking service",
    }
    token = encode( payload, JWT_SECRET, algorithm='HS256').decode('utf-8')
    return token

def unpack_response( res ):

    print( f'Response Status: {res.status_code}')

    res_json = json.loads( res.text )
    
    print('Parsed JSON HAL:\n')
    for k, v in res_json.items():
        print(f'{k}:')
        for kk, vv in v.items():

            print( f'\t{kk}:\t{vv}\n')
        

    links = res_json.get('_links')
    embedded = res_json.get('_embedded')
    if embedded:
        # msg = embedded.get('message')
        # if msg:
        #     print(msg[0])
        return links, embedded
    return links, None


def api_call( method, endpoint ):
    path = API_URL + endpoint
    title('API Call')
    print(f'URI: {path}')
    try:
        res = request_functions[ method ] (
            path,
            headers={
                'Authorization': f'Bearer {courier_data["token"]}'}
        )
    except:
        return 'Web Service is down. Wait.', 503
    return unpack_response( res )


functions = [
    show_labels,
    show_packages,
    create_package,
    change_status
]

request_functions = {
    'GET': requests.get,
    'POST': requests.post,
    'OPTIONS': requests.options,
    'PUT': requests.put
}



# TODO:
# DONE option choices come from API
# NOPE the same thing in sender
# DONE generate jwt token when sender logs in
# DONE in API check whether sender has label token
# DONE courier API calls
# DONE JWT expire time
# DONE Odporność na problemy po stronie WS
# DONE the same in Courier
# DONE Heroku
# DONE? Testing
# Refactoring (files splitting?, prints)



'''=============== Main Loop ==============='''

def main():
    

    title( 'Welcome to Pączkomat Courier App' )

    username = input('Enter your username (default is santa): ')
    if not username:
        username = 'santa'

    print(f'Logged in as {username}')
    courier_data['username'] = username
    courier_data['token'] = issue_auth_token( username )


    while True:
        links, embedded = api_call( 'GET', '/courier' )
        if embedded == 503:
            input('[503] Service is down. Wait.')
        else:
            break


    while True:

        questions = [ {
        'type': 'list',
        'name': 'main',
        'message': 'Choose an option:',
        'choices': list(links.keys())[:-1]
        }]

        answer = prompt(questions, style=custom_style)['main']
        function_id = int(answer[0])-1
        resp = functions[ function_id ]( links[answer]['href'] )
        if resp == 503:
            input('[503] Service is down. Wait.')

        # break

        


if __name__ == "__main__":
    main()
