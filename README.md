# TWITCH FULL AUTO PREDICTIONS FOR APEX LEGENDS STREAMS

## 1. Installation
This is a simple python script. You can run it from your console or an IDE of your choice.  
Make sure that the libraries imported at the beginning of the script are installed in your environment.  

## 2. First setup
For this script to work you will need to be t3 patreon sub to hugo as it uses his matchhistory API -> [link](https://www.patreon.com/hugodev/posts)  
Once you recieve your API key save it in ALS_APIkey.csv - make sure to remove the dummy text in the file first.  
Then you need to specify the variables `broadcaster` and `origin` in lines 18 and 19.  
`broadcaster` should be set to the twitch channel name that you want to run predictions in.  
`origin` needs to be set to the origin username of the monitored player (streamer). You can get it from the players ApexLegendsStatus page.  

Now you can run the script. **THIS NEXT PART HAS TO BE DONE BY THE CHANNEL OWNER.** If you are a moderator running the predictions for a streamer you have to send them the Authorization URL and they will have to send the redirect link back to you.  
On the first run you will be met with your console telling you `Authorization URL copied to clipboard. Paste it in your browser`.  
Do as you are told and open the link. You will get to the twitch-OAuth screen asking you to authorize the script to manage your channel predictions. Upon clicking "Authorize" you will be redirected to a dead link starting with `localhost://`.  
Copy this link to your clipboard. In your console you will be asked to `Paste the full redirect URl here:`. Paste the link and press Enter.  
This fetches an access and a refresh key from twitch. They will be saved to user_oauth.csv.  

Once you have gone through this process the twitch-OAuth keys will be fetched from the aforementioned .csv and automatically update if needed.

## 3. Usage
Once the first setup is done you can run the script either from your console or your preferred IDE.  
Default prediction window is 2 minutes.  
*Make sure the player you are tracking has BR Damage and Apex Kills trackers equipped on all the legends they play.* Data can only be fetched from equipped banners.  
Currently predictions on damage, rp gained and kills are possible. If you want to run predictions on pubs remove `"rp",` from `prediction_types` in line 26.  
It will automatically set up randomised predictions for your viewers to bet on and close them or cancel them, if you die before the prediction has been closed.  
Upon closure or cancellation another prediction will be set up.   

## 4. Contact  
If you need help or have feedback you can reach me on [twitter](https://twitter.com/whotookelex420) or [discord](https://discordapp.com/users/elex420#4962).  
If you want to report an issue please add it to the Issues tab right here on github.  

## 5. License  

MIT-License 2024 elex420:  
  
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.