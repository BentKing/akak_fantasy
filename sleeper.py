#!/usr/env python3

import requests
import json
user_id="1085687403316072448"
league_id="1056411750146420736"
url_base="https://api.sleeper.app/v1/"

week="1"

url1=url_base + "user/" + user_id + "/leagues/nfl/2024"
url2=url_base + "/league/" + league_id + "/matchups/" + week
def get(url):
    response_obj=requests.get(url)
    return(response_obj.text)

#print(get(url1))
matchups = get(url2)

for k in json.loads(matchups):
    for kk,vv in k.items():
        if kk == "roster_id":
            print(vv)
