# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 17:30:43 2024

@author: alex
"""

import csv
import time
import requests
import random
from requests_oauthlib import OAuth2Session
from urllib.parse import urlparse, parse_qs
import pyperclip

client_id = "1b4iweppmup6hvezqf0b2vqxmqbf2e"  #twitch API client id
broadcaster = "" #channel the commands are run in
origin = ""  #origin username of the tracked player
twitch_OAuth = "user_oauth.csv"
prediction_window = 120

with open ('client_secret.csv') as cs: #twitch API client secret
    reader = csv.reader(cs)
    for row in reader:
        client_secret = row[0]

with open ('ALS_APIkey.csv') as keyfile: #import Apexlegendsstatus api key
    reader = csv.reader(keyfile)
    for row in reader:
        ALS_API_key = row[0]
        
prediction_types = ["kills", "rp", "damage"]

###HANDLING TWITCH AUTHORIZATION
def get_OAuth_token(client_id, client_secret): #OAuth token to grant auto-predictions access to twitch API
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    data = response.json()
    
    return data['access_token'] 

def get_user_OAuth_token(client_id): #get user OAuth token
    twitch = OAuth2Session(client_id, redirect_uri="https://localhost", scope = ["channel:moderate", "user:read:email", "channel:read:predictions", "channel:manage:predictions"])
    authorization_url, _ = twitch.authorization_url("https://id.twitch.tv/oauth2/authorize")
    pyperclip.copy(authorization_url)
    print("Authorization URL copied to clipboard. Paste it in your browser")
    redirect_response = input("Paste the full redirect URL here: ")
    parsed_url = urlparse(redirect_response)
    authorization_code = parse_qs(parsed_url.query)['code'][0]
    token = twitch.fetch_token("https://id.twitch.tv/oauth2/token", code=authorization_code, client_secret=client_secret, include_client_id=True)
    access_token = token['access_token']
    refresh_token = token['refresh_token']
    with open(twitch_OAuth, "w") as tokens:
        writer = csv.writer(tokens)
        writer.writerow([access_token, refresh_token])
    return access_token

def check_user_OAuth_token(): #check twitch user OAuth token and refresh in case it's expired
    with open(twitch_OAuth) as current_token:
        reader = csv.reader(current_token)
        first_row = next(reader)  # Get the first row
        token = first_row[0]  # Get the first element of the first row
        refresh = first_row[1]
    url = "https://id.twitch.tv/oauth2/validate"
    headers  = {
        'Authorization': f'Bearer {token}'
        }   
    response = requests.get(url, headers=headers)
    data = response.json()
    if 'message' in data and 'invalid access token' in data['message'] or 'message' in data and 'missing authorization token' in data['message']:
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh,
            'client_id': client_id,
            'client_secret': client_secret
            }
        response = requests.post(url, data=params)
        data = response.json()
        if 'message' in data and 'Invalid refresh token' in data['message']:
            return get_user_OAuth_token(client_id)
        else:
            new_access_token = data['access_token']
            new_refresh_token = data['refresh_token']
            with open(twitch_OAuth, "w") as tokens:
                writer = csv.writer(tokens)
                writer.writerow([new_access_token, new_refresh_token])
            return new_access_token
    else:
        return token

def get_broadcaster_id(broadcaster, OAuth_token, client_id): #get broadcaster twitch channel id 
    url = f'https://api.twitch.tv/helix/users?login={broadcaster}'
    headers = {
        'Authorization': f'Bearer {OAuth_token}',
        'Client-ID': client_id
        }
    response = requests.get(url, headers=headers)
    data = response.json()
    if 'data' in data and len(data['data']) > 0:
        
        return data['data'][0]['id']
    else:
        return None

###HANDLING PREDICTION LOGIC    
def choose_random_prediction(): #randomly select type of next prediction
    prediction_type = random.choice(prediction_types)
    
    return prediction_type

def randomise_kill_prediction(): #randomise the kill values to bet on
    x = int(random.randrange(3, 10, 1))
    title = "How many kills next game?"
    outcome1 = str(x) + " or more"
    outcome2 = "less than " + str(x)
    
    return title, outcome1, outcome2, x

def setup_kill_prediction(user_OAuth_token, client_id, streamer_id, prediction_window): #setup returns value to bet on (x), prediction id and outcome-id's
    title, outcome1, outcome2, x = randomise_kill_prediction()
    url = 'https://api.twitch.tv/helix/predictions'
    headers = {
        'Authorization': f'Bearer {user_OAuth_token}',
        'Client-ID': client_id,
        'Content-Type': 'application/json'
        }
    data = {
        'broadcaster_id': streamer_id,
        'title': title,
        'outcomes': [{"title": outcome1}, {"title": outcome2}],
        'prediction_window': prediction_window
    }
    response = requests.post(url, headers=headers, json=data)
    prediction_id = response.json()['data'][0]['id']
    outcome1_id = response.json()['data'][0]['outcomes'][0]['id']
    outcome2_id = response.json()['data'][0]['outcomes'][1]['id']
    
    return x, prediction_id, outcome1_id, outcome2_id

def randomise_rp_prediction(): #randomise the rp values to bet on
    x = random.randrange(50, 200, 10)
    title = "How much rp will be gained next game?"
    outcome1 = str(x) + " or more"
    outcome2 = "less than " + str(x)
    
    return title, outcome1, outcome2, x

def setup_rp_prediction(): #setup returns value to bet on (x), prediction id and outcome-id's
    title, outcome1, outcome2, x = randomise_rp_prediction()
    url = 'https://api.twitch.tv/helix/predictions'
    headers = {
        'Authorization': f'Bearer {user_OAuth_token}',
        'Client-ID': client_id,
        'Content-Type': 'application/json'
        }
    data = {
        'broadcaster_id': streamer_id,
        'title': title,
        'outcomes': [{"title": outcome1}, {"title": outcome2}],
        'prediction_window': prediction_window
    }
    response = requests.post(url, headers=headers, json=data)
    prediction_id = response.json()['data'][0]['id']
    outcome1_id = response.json()['data'][0]['outcomes'][0]['id']
    outcome2_id = response.json()['data'][0]['outcomes'][1]['id']
    
    return x, prediction_id, outcome1_id, outcome2_id

def randomise_damage_prediction(): #randomise the kill values to bet on
    x = int(random.randrange(1200, 2500, 50))
    title = "How much damage next game?"
    outcome1 = str(x) + " or more"
    outcome2 = "less than " + str(x)
    
    return title, outcome1, outcome2, x

def setup_damage_prediction(): #setup returns value to bet on (x), prediction id and outcome-id's
    title, outcome1, outcome2, x = randomise_damage_prediction()
    url = 'https://api.twitch.tv/helix/predictions'
    headers = {
        'Authorization': f'Bearer {user_OAuth_token}',
        'Client-ID': client_id,
        'Content-Type': 'application/json'
        }
    data = {
        'broadcaster_id': streamer_id,
        'title': title,
        'outcomes': [{"title": outcome1}, {"title": outcome2}],
        'prediction_window': prediction_window
    }
    response = requests.post(url, headers=headers, json=data)
    prediction_id = response.json()['data'][0]['id']
    outcome1_id = response.json()['data'][0]['outcomes'][0]['id']
    outcome2_id = response.json()['data'][0]['outcomes'][1]['id']
    
    return x, prediction_id, outcome1_id, outcome2_id

def get_prediction_id():
    url = 'https://api.twitch.tv/helix/predictions'
    headers = {
        'Authorization': f'Bearer {user_OAuth_token}',
        'Client-ID': client_id,
        }
    params = {
        'broadcaster_id': streamer_id,
        }
    response = requests.get(url, headers=headers, params=params)
    
    return(response.json()['data'][0]['id'])

def get_latest_kills():
   url = "https://api.mozambiquehe.re/games"
   params = {
       'auth': ALS_API_key,
       'uid': uid,
       'limit': 1
       }
   response = requests.get(url, params=params)
   
   data = response.json()[0]['gameData']
   
   for item in data:
       if item['key'] == 'kills':
           last_game_kills = item['value']
       else: 
           None
           
   return last_game_kills  

def get_last_gamestart(): 
    url = "https://api.mozambiquehe.re/games"
    params = {
        'auth': ALS_API_key,
        'uid': uid,
        'limit': 2
        }
    response = requests.get(url, params=params)
    last_game_start = response.json()[0]['gameStartTimestamp']
            
    return last_game_start  

def get_als_uid():
    url = "https://api.mozambiquehe.re/nametouid"
    params = {
        "auth": "938949c327a9cdd159327e6b8aeb3d7e",
        "player": f"{origin}",
        "platform": "PC"
    }
    response = requests.get(url, params=params)
    uid = response.json()['uid']
    
    return uid

def get_rp_change():
    url = "https://api.mozambiquehe.re/games"
    params = {
        'auth': ALS_API_key,
        'uid': uid,
        'limit': 1
        }
    response = requests.get(url, params=params)
    rp_change = response.json()[0]['BRScoreChange']
    
    return rp_change

def get_latest_damage():
   url = "https://api.mozambiquehe.re/games"
   params = {
       'auth': ALS_API_key,
       'uid': uid,
       'limit': 1
       }
   response = requests.get(url, params=params)
   
   data = response.json()[0]['gameData']
   
   for item in data:
       if item['key'] == 'damage':
           last_game_kills = item['value']
       else: 
           None
           
   return last_game_kills  

def close_prediction(outcome):
    if outcome == 1:
        url = 'https://api.twitch.tv/helix/predictions'
        headers = {
            'Authorization': f'Bearer {user_OAuth_token}',
            'Client-Id': client_id,
            'Content-Type': 'application/json'
            }
        data = {
            'broadcaster_id': streamer_id,
            'id': prediction_id,
            'status': "RESOLVED",
            'winning_outcome_id': outcome1_id
            }
        requests.patch(url, headers=headers, json=data)
    if outcome == 2:
        url = 'https://api.twitch.tv/helix/predictions'
        headers = {
            'Authorization': f'Bearer {user_OAuth_token}',
            'Client-Id': client_id,
            'Content-Type': 'application/json'
            }
        data = {
            'broadcaster_id': streamer_id,
            'id': prediction_id,
            'status': "RESOLVED",
            'winning_outcome_id': outcome2_id
            }
        requests.patch(url, headers=headers, json=data)

def cancel_prediction():
    url = 'https://api.twitch.tv/helix/predictions'
    headers = {
        'Authorization': f'Bearer {user_OAuth_token}',
        'Client-Id': client_id,
        }
    data = {
        'broadcaster_id': streamer_id,
        'id': prediction_id,
        'status': "CANCELED",
        }
    response = requests.patch(url, headers=headers, json=data)
    
    return(response)
    
if __name__ =="__main__":
    OAuth_token = get_OAuth_token(client_id, client_secret)
    streamer_id = get_broadcaster_id(broadcaster, OAuth_token, client_id)
    user_OAuth_token = check_user_OAuth_token()
    uid = get_als_uid()
    prediction_type = choose_random_prediction()
    previous_start_time = get_last_gamestart()
    try:
        prediction_id = get_prediction_id()
        cancel_prediction()
    except:
        pass
    while True:
        user_OAuth_token = check_user_OAuth_token()
        prediction_type = choose_random_prediction()
        if "kills" in prediction_type:
            x, prediction_id, outcome1_id, outcome2_id = setup_kill_prediction(user_OAuth_token, client_id, streamer_id, prediction_window)
            starttime = time.time()
            while True:
                if previous_start_time != get_last_gamestart():
                    if int(time.time() - starttime) >= prediction_window:
                        if get_latest_kills() >= x:
                            close_prediction(1)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed kill prediction")
                            break
                        elif get_latest_kills() <x:
                            close_prediction(2)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed kill prediction")
                            break
                    elif int(time.time() - starttime) < prediction_window:
                        cancel_prediction()
                        prediction_type = "none"
                        previous_start_time = get_last_gamestart()
                        print("cancelled kill prediction")
                        break
                else:
                    time.sleep(30)
                    print("running")
                        
        elif "rp" in prediction_type:
            x, prediction_id, outcome1_id, outcome2_id = setup_rp_prediction()
            starttime = time.time()
            while True:
                if previous_start_time != get_last_gamestart():
                    if int(time.time() - starttime) >= prediction_window:
                        if get_rp_change() >= x:
                            close_prediction(1)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed rp prediction")
                            break
                        elif get_rp_change() < x:
                            close_prediction(2)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed rp prediction")
                            break
                    elif int(time.time() - starttime) < prediction_window:
                        cancel_prediction()
                        prediction_type = "none"
                        previous_start_time = get_last_gamestart()
                        print("cancelled rp prediction")
                        break
                else:
                    time.sleep(30)
                    print("running")
        
        elif "damage" in prediction_type:
            x, prediction_id, outcome1_id, outcome2_id = setup_damage_prediction()
            starttime = time.time()
            while True:
                if previous_start_time != get_last_gamestart():
                    if int(time.time() - starttime) >= prediction_window:
                        if get_latest_damage() >= x:
                            close_prediction(1)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed damage prediction")
                            break
                        elif get_latest_damage() < x:
                            close_prediction(2)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed damage prediction")
                            break
                    elif int(time.time() - starttime) < prediction_window:
                        cancel_prediction()
                        prediction_type = "none"
                        previous_start_time = get_last_gamestart()
                        print("cancelled damage prediction")
                        break
                else:
                    time.sleep(30)
                    print("running")
        else:
            continue
                
        
