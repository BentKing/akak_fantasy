#!/usr/env python3

import requests
import os
import json

# Set this to current week
week=1

start_match=(week-1) * 8
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

def call_espn_api():
    lid="<league-id>"
    api_base="https://lm-api-reads.fantasy.espn.com/apis/v3/"
    query="games/ffl/seasons/2024/segments/0/leagues/"
    espn_s2="<long-web-string>"
    swid="<hexadecimal-string>"
    cookies = {"swid" : swid, "espn_s2" : espn_s2}
    # Get Data from ESPN
    espn_req = requests.get(api_base + query + lid + "?view=modular&view=mNav&view=mMatchupScore&view=mScoreboard&view=mSettings&view=mTopPerformers&view=mTeam", cookies=cookies)
    return(espn_req.text)

# Info on JSON dict
# cat output.json | jq .schedule[].home.teamId
# Output appears to be schedule[].home and schedule[].away are all individual team-game objects
# cat output.json | jq .schedule[0].away.pointsByScoringPeriod
# Likely schedule is a list of all matchups. We have 7 week 1 each with a home and away. Likely week 2 will be 8-15

# Schedule is setup as a grouping of 7 matchups (week_number - 1)*8 - week_number
# This creates a range ie. week 3 is groupings
espn_data = json.loads(call_espn_api())

# Generate matchup list
matchup_list=[]
for i in list(week_nums):
    team1 = espn_data['schedule'][int(i)]['home']['teamId']
    team2 = espn_data['schedule'][int(i)]['away']['teamId']
    matchup_list.append((team1,team2))

def points():
    points_dict = {}
    points_for = [] 
    points_against = []
    for i in list(week_nums):
        points_dict[espn_data['schedule'][int(i)]['home']['teamId']] = espn_data['schedule'][int(i)]['home']['pointsByScoringPeriod']['1']
        points_dict[espn_data['schedule'][int(i)]['away']['teamId']] = espn_data['schedule'][int(i)]['away']['pointsByScoringPeriod']['1']
    for player in excel_order:
        num_of_pos = person_dict[player]
        points_for.append(points_dict[num_of_pos])
    for player in excel_order:
        num_of_pos = person_dict[player]
        for grouping in matchup_list:
            if num_of_pos in grouping:
                for item_grouping in grouping:
                    if item_grouping != num_of_pos:
                        points_against.append(points_dict[item_grouping])
    return(points_for,points_against)

# Final Output
pf,pa = points()

# do pointswap to put Ben in Hell
revised_pa = []
for item in pa[1:]:
    revised_pa.append(item)
revised_pa.append(pa[0])
print("Points For:")
print("===========")
for score in pf:
    print(score)
print("\n*$*$*\n")
print("Points Against:")
print("===========")
for i in range(0,len(revised_pa)):
    if i == len(revised_pa) - 1:
        print("You Are Now Entering Hell")
    print(revised_pa[i])
