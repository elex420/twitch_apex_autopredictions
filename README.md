# TWITCH FULL AUTO PREDICTIONS FOR APEX LEGENDS STREAMS

## 1. Installation
This is a simple python script. Once you download this repo you can run it from your console or an IDE of your choice.  
Make sure that the libraries imported at the beginning of the script are installed in your environment.  

## 2. First setup
For this script to work you will need to be [t3 patreon sub to hugo](https://www.patreon.com/hugodev/posts) as it uses his matchhistory API.  
Once you recieve your ApexLegendsAPI key save it in ALS_APIkey.csv - make sure to remove the dummy text in the file first.  
Then you will also need the client_secret key. Message elex420 for your key (see contact information below). 
You can change the amount of time that the prediction is open to bet on. For that change `prediction_window` in line 20. Accepted values are 30, 60, 120, 300, 600, 900, 1200 or 1800 seconds. This should be chosen depending on the length of queue times.  

Now you can run the script. You will be asked to input the twitch channel name that you want to run predictions in as well as the origin username of the player that you want to track.  
*THIS NEXT PART HAS TO BE DONE BY THE CHANNEL OWNER.* If you are a moderator running the predictions for a streamer you have to send them the Authorization URL and they will have to send the redirect link back to you.  
On the first run you will be met with your console telling you `Authorization URL copied to clipboard. Paste it in your browser`.  
Do as you are told and open the link. You will get to the twitch-OAuth screen asking you to authorize the script to manage your channel predictions. Upon clicking "Authorize" you will be redirected to a dead link starting with `localhost://`.  
Copy this link to your clipboard. In your console you will be asked to `Paste the full redirect URl here:`. Paste the link and press Enter.  
This fetches an access and a refresh key from twitch. They will be saved to user_oauth.csv.  

Once you have gone through this process the twitch-OAuth keys will be fetched from the aforementioned .csv and automatically update if needed.

## 3. Usage
Once the first setup is done you can run the script either from your console or your preferred IDE. Every time you run the script it will ask you to input the twitch channel and the origin username.  
*Make sure the player you are tracking has BR Damage, Apex Kills and Apex Wins trackers equipped on all the legends they play.* Data can only be fetched from equipped banners.  
Currently predictions on damage, rp gained, kills and wins are possible. If you want to run predictions on pubs remove `"rp",` from `prediction_types` in line 26.  
It will automatically set up randomised predictions for your viewers to bet on and either close them or cancel them, if you die before the prediction has been closed.  
Upon closure or cancellation another prediction will be set up.   

## 4. Contact  
If you need help or have feedback you can reach me on [twitter](https://twitter.com/whotookelex420) or [discord](https://discordapp.com/users/elex420#4962).  
If you want to report an issue please add it to the Issues tab right here on github.  

## 5. License  

MIT-License elex420 2024:  
  
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.