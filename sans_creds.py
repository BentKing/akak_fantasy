#!/usr/env python3

import requests
import os
import json
import random
import decimal
import time
import csv
import shutil
import datetime
from datetime import timedelta

# Returns current NFL Week based on date.
from dateutil import rrule
import datetime
def weeks_between(start_date, end_date):
    weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
    return weeks.count()

# Wednesday before football starts
nfl_start_date=datetime.datetime(2024,9,4)
week = weeks_between(nfl_start_date, datetime.datetime.today())
players = 14
dest_filepath = "/mnt/d/Desktop/Side_Projects/Fantasy/2024/full_week_data.csv"
full_pull=False #Set this if you want to pull every week from ESPN not just current week
num_uniq_rosters = week * players

# Authentication Data
lid=""
api_base="https://lm-api-reads.fantasy.espn.com/apis/v3/"
query="games/ffl/seasons/2024/segments/0/leagues/"
espn_s2=""
swid=""
cookies = {"swid" : swid, "espn_s2" : espn_s2}

# Match Team ID to Name
person_dict = {"ben":11, \
               "tyler":4, \
               "austin":12, \
               "jackson":6, \
               "ethan":14,\
               "reid":9,\
               "chase":7,\
               "khyler":13,\
               "liam":3,\
               "rohan":10,\
               "adam":2,\
               "logan":8,\
               "ian":1,\
               "cooper":5}

# Get current week data from ESPN
def call_espn_api(week_num):
    espn_req = requests.get(api_base + query + lid + "?view=mMatchup&view=mMatchupScore",params={'scoringPeriodId': week_num, 'matchupPeriodId': week_num}, cookies=cookies)
    return(espn_req.text)

# Lookup team name from team_id
def reverse_lookup(team_id):
    for k,v in person_dict.items():
        if v == team_id:
            return(k)

#.schedule[0].home.rosterForCurrentScoringPeriod.entries[0].playerPoolEntry.appliedStatTotal
def convert_to_position(eligibleSlots):
    if 16 in eligibleSlots:
        return("Defense")
    elif 17 in eligibleSlots:
        return("Kicker")
    elif 0 in eligibleSlots:
        return("Quarterback")
    elif 2 in eligibleSlots:
        return("Runningback")
    elif 6 in eligibleSlots:
        return("TightEnd")
    elif 4 in eligibleSlots:
        return("Receiver")
    else:
        return("TaysomHill")

# Parse individual matchup data ie. player scores for a single roster+week combo
def get_team_data_for_matchup_num(espn_data, uniq_matchup):
    player_list = []
    matchup_num = convert_to_raw_match(uniq_matchup)[0]
    home_away = convert_to_raw_match(uniq_matchup)[1] 
    week_num = (uniq_matchup // players) + 1
    for item in espn_data[str(week_num)]['schedule'][matchup_num][home_away]['rosterForMatchupPeriod']['entries']:
        player_dict = {}
        player_dict['team_id'] = espn_data[str(week_num)]['schedule'][matchup_num][home_away]['teamId']
        player_dict['points'] = round(item['playerPoolEntry']['appliedStatTotal'],2)
        player_dict['position'] = convert_to_position(item['playerPoolEntry']['player']['eligibleSlots'])
        player_dict['name'] = item['playerPoolEntry']['player']['fullName']
        player_dict['curr_team_id'] = item['playerPoolEntry']['onTeamId'] # If they have since been dropped/trade,this sets to new # regardless of old team
        player_dict['uniq_matchup'] = uniq_matchup
        player_list.append(player_dict)
    return(player_list)

'''
ESPN has lots of data in format: "Match 13, Home Team";
referring to the "home team" of the 6th match of the 2nd week (each week has 14/2).
By doubling the val and adding 1, we can create a unique match number meaning 
'the roster for X team at a particular point in time', which is much more useful. 
Can convert back and forth at will.
'''
def convert_to_uniq_match(matchup_num, home_away):
    if home_away == "away":
        return(( matchup_num * 2 ) + 1)
    else:
        return(( matchup_num *2 ))

def convert_to_raw_match(uniq_matchup):
    if uniq_matchup % 2 == 0:
        return(uniq_matchup // 2, "home")
    else:
        return(uniq_matchup //2, "away")

#
####################################################
####################### MAIN #######################
####################################################
#

if full_pull=True:
    ## NUCLEAR OPTION, HITS ESPN ONCE PER WEEK ACCUMULATED, SLOW ###
    espn_data_full={}
    for item in range(1,week+1):
       week_data = call_espn_api(item)
       notabot = decimal.Decimal(random.randrange(0, 500))/100
       print("sleeping")
       time.sleep(5+notabot)
       espn_data_full[item]=json.loads(week_data)
    
    f3 = open('full_weekdata.txt','w')
    f3.write(json.dumps(espn_data_full))
    f3.close()

# Pull existing dataset
f2 = open("full_weekdata.txt", "r")
raw_data=json.loads(f2.read())
f2.close()

# Get current week data (single call only) and flush to disk
new_data = call_espn_api(week)
raw_data[str(week)] = json.loads(new_data)
espn_file = open("full_weekdata.txt", "w")
espn_file.write(json.dumps(raw_data))
espn_file.close()

# For every matchup in data, parse player data
big_list = []
for uniq_matchup in range(0,num_uniq_rosters):
    big_list.append(get_team_data_for_matchup_num(raw_data,uniq_matchup))

# Define Field Names
csv_raw=[["Name","Team_ID","Player","Position","Week","Points","Matchup","Opponent"]]
#For every player line-item, append to a big list and dump to csv
for matchup in big_list:
    for player in matchup:
        name = reverse_lookup(player["team_id"])
        week_of_matchup = (player["uniq_matchup"] // players )+ 1
        if player["uniq_matchup"] % 2 == 0:
            opponent = player["uniq_matchup"] + 1
        else:
            opponent = player["uniq_matchup"] - 1
        csv_raw.append([name, player["team_id"], player["name"], player["position"], week_of_matchup, player["points"], player["uniq_matchup"], opponent])
    with open('full_week_data.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(csv_raw)

# Move data to ultimate destination
shutil.copy('full_week_data.csv',dest_filepath)
