import csv
import requests
from requests_oauthlib import OAuth2Session
from urllib.parse import urlparse, parse_qs
from pyperclip import copy
import websocket
import time
import threading
import json

client_id = "1b4iweppmup6hvezqf0b2vqxmqbf2e"  #twitch API client id
client_secret = "c2qscw33co4vvkqvqkkrnx9m9h9v49"
twitch_OAuth = "mod_oauth.csv"
        

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
                                                                                 "channel:manage:predictions", "user:read:chat", 
                                                                                 "user:write:chat", "user:bot", "channel:bot", "whispers:read"
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
###SENDING MESSAGE IN TWITCH CHAT
def send_message(message):
    url = 'https://api.twitch.tv/helix/chat/messages'
    headers = {
        'Authorization': f'Bearer {user_OAuth_token}',
        'Client-Id': client_id,
        'Content-Type': 'application/json'
        }
    data = {
        'broadcaster_id': streamer_id,
        'sender_id': sender_id,
        'message': message
        }
    response = requests.post(url, headers=headers, json=data)
    print(response.json())

###WEBSOCKET SETUP
def create_websocket():
    return websocket.WebSocketApp("wss://pubsub-edge.twitch.tv",
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close)

def on_message(ws, message): 
    message_data = json.loads(json.loads(json.loads(message)['data']['message'])['data'])
    message_id = message_data['message_id']
    thread = message_data['thread_id']
    sender = message_data['tags']['login']
    content = message_data['body']
    print("THREAD: ", thread,"SENDER: ", sender, "CONTENT: ", content, "ID: ", message_id)
    
    if content == "!startgamba" or content == "!stopgamba":    
        with open('message_data.csv', 'w', newline='') as csvfile:
            fieldnames = ['message_id', 'thread', 'sender', 'content']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'message_id': message_id, 'thread': thread, 'sender': sender, 'content': content})
    else: 
        pass
    
    return message_id, thread, sender, content
    
def on_error(ws, error):
    print("Error: ", error)
    reconnect(ws)

def reconnect(ws):
    time.sleep(5)
    ws = create_websocket()
    ws.run_forever()

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    def run(*args):
        # Listen to whispers for a specific user ID
        data = {
            "type": "LISTEN",
            "nonce": "44h1k13746815ab1r2",
            "data": {
                "topics": [f"whispers.{sender_id}"],
                "auth_token": user_OAuth_token
            }
        }
        ws.send(json.dumps(data))
        while True:
            time.sleep(240)
            ws.send(json.dumps({"type": "PING"}))
    threading.Thread(target=run).start()


if __name__ == "__main__":
    broadcaster = "vUnlucky"
    sender = "elex420"
    OAuth_token = get_app_OAuth_token(client_id, client_secret) #authorizing this script
    streamer_id = get_broadcaster_id(broadcaster, OAuth_token, client_id) #
    sender_id = get_broadcaster_id(sender, OAuth_token, client_id)
    user_OAuth_token = check_user_OAuth_token()
    #send_message(" ")
    ws = create_websocket()
    ws.on_open = on_open
    ws.run_forever()
    