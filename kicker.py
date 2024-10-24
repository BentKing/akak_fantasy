#!/usr/env python3

import requests
import os
import json
import random
import decimal
import time
import csv


# Set this to current week
week = 7
start_match=(week-1) * 7
end_match=start_match + 7
week_nums = range(start_match, end_match)
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

excel_order=["ben","cooper","khyler","ian","liam","reid","chase","jackson","austin","ethan","logan","tyler","adam","rohan"]

def call_espn_api(week_num):
    lid=""
    api_base="https://lm-api-reads.fantasy.espn.com/apis/v3/"
    query="games/ffl/seasons/2024/segments/0/leagues/"
    espn_s2=""
    swid=""
    cookies = {"swid" : swid, "espn_s2" : espn_s2}
    # Get Data from ESPN
    espn_req = requests.get(api_base + query + lid + "?view=mMatchup&view=mMatchupScore",params={'scoringPeriodId': week_num, 'matchupPeriodId': week_num}, cookies=cookies)
    return(espn_req.text)

# Schedule is setup as a grouping of 7 matchups (week_number - 1)*8 - week_number
# This creates a range ie. week 3 is groupings

f2 = open("full_weekdata.txt", "r")
espn_data=json.loads(f2.read())
f2.close()


### NUCLEAR OPTION, HITS ESPN ONCE PER WEEK ACCUMULATED, SLOW ###
#espn_data_full={}
#for item in range(1,week+1):
#   week_data = call_espn_api(item)
#   notabot = decimal.Decimal(random.randrange(0, 500))/100
#   print("sleeping")
#   time.sleep(5+notabot)
#   espn_data_full[item]=json.loads(week_data)
#
#f3 = open('full_weekdata.txt','w')
#f3.write(json.dumps(espn_data_full))
#f3.close()

## END NUCLEAR OPTION ##

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

def get_team_data_for_matchup_num(uniq_matchup):
    player_list = []
    matchup_num = convert_to_raw_match(uniq_matchup)[0]
    print(matchup_num)
    home_away = convert_to_raw_match(uniq_matchup)[1] 
    print(home_away)
    week_num = (uniq_matchup // 14) + 1
    print(week_num)
    for item in espn_data[str(week_num)]['schedule'][matchup_num][home_away]['rosterForMatchupPeriod']['entries']:
        player_dict={}
        player_dict['team_id'] = espn_data[str(week_num)]['schedule'][matchup_num][home_away]['teamId']
        player_dict['points'] = round(item['playerPoolEntry']['appliedStatTotal'],2)
        player_dict['position'] = convert_to_position(item['playerPoolEntry']['player']['eligibleSlots'])
        player_dict['name'] = item['playerPoolEntry']['player']['fullName']
        player_dict['curr_team_id'] = item['playerPoolEntry']['onTeamId'] # If they have since been dropped/trade,this sets to new # regardless of old team
        player_dict['uniq_matchup'] = uniq_matchup
        player_list.append(player_dict)
    return(player_list)


# ESPN has lots of data in format: match 13, home team, referring to the "home team" of the 6th match of the 2nd week (each week has 14/2). By doubling the val and adding 1, we can create a unique match number meaning 'the roster for X team at a particular point in time, which is much more useful. Can convert back and forth at will.
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

# TODO make this append to data each week
num_uniq_rosters = week * 14

#uncomment

big_list = []
for uniq_matchup in range(0,num_uniq_rosters):
    big_list.append(get_team_data_for_matchup_num(uniq_matchup))

csv_raw=[["Name","Team_ID","Player","Position","Week","Points","Matchup","Opponent"]]
for matchup in big_list:
    for player in matchup:
        name = reverse_lookup(player["team_id"])
        week_of_matchup = (player["uniq_matchup"] // 14 )+ 1
        if player["uniq_matchup"] % 2 == 0:
            opponent = player["uniq_matchup"] + 1
        else:
            opponent = player["uniq_matchup"] - 1
        csv_raw.append([name, player["team_id"], player["name"], player["position"], week_of_matchup, player["points"], player["uniq_matchup"], opponent])
    with open('full_week_data.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(csv_raw)


# TODO points_for, points_against
# TODO auto-create CSV
