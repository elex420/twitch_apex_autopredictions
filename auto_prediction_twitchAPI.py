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
from pyperclip import copy

client_id = "1b4iweppmup6hvezqf0b2vqxmqbf2e"  #twitch API client id
twitch_OAuth = "user_oauth.csv"
prediction_window = 300


with open ('client_secret.csv') as cs: #twitch API client secret
    reader = csv.reader(cs)
    for row in reader:
        client_secret = row[0]

with open ('ALS_APIkey.csv') as keyfile: #import Apexlegendsstatus api key
    reader = csv.reader(keyfile)
    for row in reader:
        ALS_API_key = row[0]
        

###HANDLING TWITCH AUTHORIZATION
def get_app_OAuth_token(client_id, client_secret): #OAuth token to grant auto-predictions access to twitch API
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    data = response.json()
    
    return data['access_token'] 

def get_user_OAuth_token(client_id): #get user OAuth token and write it to user_oauth.csv
    twitch = OAuth2Session(client_id, redirect_uri="https://localhost", scope = ["channel:moderate", "user:read:email", 
                                                                                 "channel:read:predictions", 
                                                                                 "channel:manage:predictions"
                                                                                 ]
                           )
    authorization_url, _ = twitch.authorization_url("https://id.twitch.tv/oauth2/authorize")
    copy(authorization_url)
    print("Authorization URL copied to clipboard. Paste it in your browser")
    redirect_response = input("Paste the full redirect URL here: ")
    parsed_url = urlparse(redirect_response)
    authorization_code = parse_qs(parsed_url.query)['code'][0]
    token = twitch.fetch_token("https://id.twitch.tv/oauth2/token", 
                               code=authorization_code, 
                               client_secret=client_secret,
                               include_client_id=True)
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

###HANDLING PREDICTION LOGIC - TWITCH API  
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

def choose_random_prediction(): #randomly return type of next prediction, but not the one from the game before
    while True:
        prediction_type = random.choice(prediction_types)
        if prediction_type == last_prediction:
            continue
        elif prediction_type != last_prediction:
            
            return prediction_type

#randomising values to gamble on    
def randomise_kill_prediction(): #randomise the kill values to bet on
    x = int(random.randrange(3, 10, 1))
    title = "How many kills next game?"
    outcome1 = str(x) + " or more"
    outcome2 = "less than " + str(x)
    
    return title, outcome1, outcome2, x

def randomise_rp_prediction(): #randomise the rp values to bet on
    x = random.randrange(50, 200, 10)
    title = "How much rp will be gained next game?"
    outcome1 = str(x) + " or more"
    outcome2 = "less than " + str(x)
    
    return title, outcome1, outcome2, x

def randomise_damage_prediction(): #randomise the kill values to bet on
    x = int(random.randrange(1200, 2500, 50))
    title = "How much damage next game?"
    outcome1 = str(x) + " or more"
    outcome2 = "less than " + str(x)
    
    return title, outcome1, outcome2, x

def randomise_win_prediction(): 
    title = "Win next game?"
    outcome1 = "yes"
    outcome2 = "no"
    
    return title, outcome1, outcome2

#communicating with twitch api to setup/close predictions
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

def setup_win_prediction(): #setup returns value to bet on (x), prediction id and outcome-id's
    title, outcome1, outcome2 = randomise_win_prediction()
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
    
    return prediction_id, outcome1_id, outcome2_id

def close_prediction(outcome): #resolve prediction; outcome 1 = believers, outcome 2 = doubters
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

def cancel_prediction(): #cancel prediction and return points
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

### GETTING GAME DATA FROM APEX LEGENDS API
def get_last_gamestart(): #returns start timestamp of the latest gamedata file
    url = "https://api.mozambiquehe.re/games"
    params = {
        'auth': ALS_API_key,
        'uid': uid,
        'limit': 2
        }
    response = requests.get(url, params=params)
    last_game_start = response.json()[0]['gameStartTimestamp']
            
    return last_game_start  
      
def get_als_uid(): #returns ALS uid of the player input into "origin"
    url = "https://api.mozambiquehe.re/nametouid"
    params = {
        "auth": ALS_API_key,
        "player": f"{origin}",
        "platform": "PC"
    }
    response = requests.get(url, params=params)
    uid = response.json()['uid']
    
    return uid

def get_latest_kills(): #returns amount of kills found in latest game data file
    url = "https://api.mozambiquehe.re/games"
    params = {
        'auth': ALS_API_key,
        'uid': uid,
        'limit': 1
        }
    response = requests.get(url, params=params)

    data = response.json()[0]['gameData']
    if len(data) != 0:
        for item in data:
            if "kills" in item['key'] and "arena" not in item['key']:
                last_game_kills = item['value']
                break
            else:
                last_game_kills = "not found"
    else:
        last_game_kills = "not found"
        
    return last_game_kills  

def get_rp_change(): #returns rp change found in latest game data file
    url = "https://api.mozambiquehe.re/games"
    params = {
        'auth': ALS_API_key,
        'uid': uid,
        'limit': 1
        }
    response = requests.get(url, params=params)
    rp_change = response.json()[0]['BRScoreChange']
    
    return rp_change

def get_latest_damage(): #returns damage found in latest game data file
    url = "https://api.mozambiquehe.re/games"
    params = {
           'auth': ALS_API_key,
           'uid': uid,
           'limit': 5
           }
    response = requests.get(url, params=params)
       
    data = response.json()[0]['gameData']
    if len(data) != 0:
       for item in data:
           if "damage" in item['key'] and "arena" not in item['key'] and "ultimate" not in item['key']:
               last_game_damage = item['value']
               break
           else: 
               last_game_damage = "not found"
    else:
         last_game_damage = "not found"
              
    return last_game_damage 

def get_latest_win(): #returns wins found in latest game data file
    url = "https://api.mozambiquehe.re/games"
    params = {
        'auth': ALS_API_key,
        'uid': uid,
        'limit': 1
        }
    response = requests.get(url, params=params)

    data = response.json()[0]['gameData']
    if len(data) != 0:
        for item in data:
            if "win" in item['key'] and "arena" not in item['key']:
                last_game_win = item['value']
                break
            else: 
                last_game_win = "not found"
    else:
        last_game_win = "not found"
  
    return last_game_win


if __name__ =="__main__":
    broadcaster = input("What is the twitch channel name that you want to run predictions in? (confirm by hitting Enter) ") #channel the commands are run in
    origin = input("What is the origin username of the player you want to track? (confirm by hitting Enter) ")  #origin username of the tracked player
    while True:
        mode = input("Is ranked being played? (y/n) ")
        if mode == "y" or mode == "yes":
            prediction_types = ["kills", "rp", "damage", "win"]
            break
        elif mode == "n" or mode == "no":
            prediction_types = ["kills", "damage", "win"]
            break
        else:
            print("Invalid input. ")
            continue
    OAuth_token = get_app_OAuth_token(client_id, client_secret) #authorizing this script
    streamer_id = get_broadcaster_id(broadcaster, OAuth_token, client_id) #
    user_OAuth_token = check_user_OAuth_token()
    uid = get_als_uid()
    last_prediction = "none"
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
            print("kill prediction setup")
            last_prediction = prediction_type
            x, prediction_id, outcome1_id, outcome2_id = setup_kill_prediction(user_OAuth_token, client_id, streamer_id, prediction_window)
            starttime = time.time()
            while True:
                if previous_start_time != get_last_gamestart():
                    if int(time.time() - starttime) >= (prediction_window + 45):
                        if get_latest_kills() == "not found":
                            cancel_prediction()
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("prediction cancelled - kills not found - equip legend kills tracker")
                            break
                        elif get_latest_kills() >= x:
                            close_prediction(1)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed kill prediction - 1")
                            time.sleep(10)
                            break
                        elif get_latest_kills() <x:
                            close_prediction(2)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed kill prediction - 2")
                            time.sleep(10)
                            break
                    elif int(time.time() - starttime) < (prediction_window + 45):
                        cancel_prediction()
                        prediction_type = "none"
                        previous_start_time = get_last_gamestart()
                        print("cancelled kill prediction")
                        break
                else:
                    time.sleep(30)
                        
        elif "rp" in prediction_type:
            print("rp prediction setup")
            last_prediction = prediction_type
            x, prediction_id, outcome1_id, outcome2_id = setup_rp_prediction()
            starttime = time.time()
            while True:
                if previous_start_time != get_last_gamestart():
                    if int(time.time() - starttime) >= (prediction_window + 45):
                        if get_rp_change() >= x:
                            close_prediction(1)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed rp prediction - 1")
                            time.sleep(10)
                            break
                        elif get_rp_change() < x:
                            close_prediction(2)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed rp prediction - 2")
                            break
                    elif int(time.time() - starttime) < (prediction_window + 45):
                        cancel_prediction()
                        prediction_type = "none"
                        previous_start_time = get_last_gamestart()
                        print("cancelled rp prediction")
                        time.sleep(10)
                        break
                else:
                    time.sleep(30)
        
        elif "damage" in prediction_type:
            print("damage prediction setup")
            last_prediction = prediction_type
            x, prediction_id, outcome1_id, outcome2_id = setup_damage_prediction()
            starttime = time.time()
            while True:
                if previous_start_time != get_last_gamestart():
                    if int(time.time() - starttime) >= (prediction_window + 45):
                        if get_latest_damage() == "not found":
                            cancel_prediction()
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("prediction cancelled - damage not found - equip legend damage tracker")
                            break
                        elif get_latest_damage() >= x:
                            close_prediction(1)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed damage prediction - 1")
                            time.sleep(10)
                            break
                        elif get_latest_damage() < x:
                            close_prediction(2)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed damage prediction - 2")
                            time.sleep(10)
                            break
                    elif int(time.time() - starttime) < (prediction_window + 45):
                        cancel_prediction()
                        prediction_type = "none"
                        previous_start_time = get_last_gamestart()
                        print("cancelled damage prediction")
                        break
                else:
                    time.sleep(30)
                    
        elif "win" in prediction_type:
            print("win prediction setup")
            last_prediction = prediction_type
            prediction_id, outcome1_id, outcome2_id = setup_win_prediction()
            starttime = time.time()
            while True:
                if previous_start_time != get_last_gamestart():
                    if int(time.time() - starttime) >= (prediction_window + 45):
                        if get_latest_win() == "not found":
                            cancel_prediction()
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("prediction cancelled - wins not found - equip legend wins tracker")
                            break
                        elif get_latest_win() == 1:
                            close_prediction(1)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed win prediction - 1")
                            time.sleep(10)
                            break
                        elif get_latest_win() == 0:
                            close_prediction(2)
                            prediction_type = "none"
                            previous_start_time = get_last_gamestart()
                            print("closed win prediction - 2")
                            time.sleep(10)
                            break
                    elif int(time.time() - starttime) < (prediction_window + 45):
                        cancel_prediction()
                        prediction_type = "none"
                        previous_start_time = get_last_gamestart()
                        print("cancelled win prediction")
                        break
                else:
                    time.sleep(30)
        
        else:
            continue
                
        
