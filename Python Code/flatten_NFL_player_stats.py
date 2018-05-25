#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 24 12:54:49 2018

@author: ejreidelbach

:DESCRIPTION:
    - This script will read in scraped JSONs from NFL.com and flatten the nested
        portions of those JSON files (the career and situational stats) which
        are currently stored in lists. This script will unpack those nested 
        lists and flatten them such that every variable is placed in its own
        column whereas every player will be in his own row.

:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import json
import pandas as pd
import os
import copy
from datetime import datetime
import math

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
# positions for which stats can be obtained
position_list = ['QUARTERBACK',
                 'RUNNING_BACK',
                 'WIDE_RECEIVER',
                 'TIGHT_END',
                 'DEFENSIVE_LINEMAN',
                 'LINEBACKER',
                 'DEFENSIVE_BACK',
                 'PUNTER',
                 'FIELD_GOAL_KICKER',
                 ]

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/PlayerStats')

# Iterate over every position folder
#for position in position_list:
#    os.chdir(r'/home/ejreidelbach/projects/NFL/Data/PlayerStats/' + position)

os.chdir(r'/home/ejreidelbach/projects/NFL/Data/PlayerStats/' + position)    
position = 'WIDE_RECEIVER'

# Read in all player data from the available JSON files
files = [f for f in os.listdir('.') if f.endswith(('.json'))]
files = sorted(files)

stat_list = []
for file in files:
    with open(file, 'r') as f:
        jsonFile = json.load(f)   
        for player in jsonFile:
            stat_list.append(player)
            
# Unpack nested career data and situational data for each player
stat_list_flattened = []
for row in stat_list:
    # create a deep copy of the row
    player = copy.deepcopy(row)
    
    # pop off the stats_annual and stats_situational elements so that we
    #   can iterate over them and add their contents back to the basic player info
    try:
        stats_annual = player.pop('stats_annual')
    except:
        print('No Annaul stats found for Player #: ' + str(stat_list.index(row)) + \
              ' - ' + player['name_first'] + ' ' + player['name_last'])
    stats_situational = player.pop('stats_situational')

    # Unpack nested career and situational data by year
    import itertools
    stats_combined = list(itertools.zip_longest(stats_annual, stats_situational, fillvalue=''))
    for annual, situation in stats_combined:
        yearPlayer = {}
        yearPlayer.update(player)
        yearPlayer.update(annual)
        yearPlayer.update(situation)
        
        # Calculate player age (12/31 of the given year - player's bday)
        d1 = datetime.strptime(yearPlayer['birthday'], "%m/%d/%Y")
        d2 = '12/31/' + yearPlayer['year']
        d2 = datetime.strptime(d2, "%m/%d/%Y")
        days_between = math.floor(abs((d2-d1).days)/365)
        yearPlayer['age'] = days_between
        
        stat_list_flattened.append(yearPlayer)
#        else:
#            print('Player #: ' + str(stat_list.index(row)) + ' -- ' + \
#                  player['name_first'] + ' ' + player['name_last'] + \
#                  ': Years do not match...Annual: ' + annual['year'] \
#                  + ' Situation: ' + situation['year'])               

# Output the flattened list to a CSV
filename = r'/home/ejreidelbach/projects/NFL/Data/PlayerStats/' + position + '.json'
with open(filename, 'wt') as out:
    json.dump(stat_list_flattened, out, sort_keys=True, indent=4, separators=(',', ': '))

# Push the flattened list into a Pandas Dataframe and output it to a CSV
df = pd.DataFrame(stat_list_flattened)
filename = r'/home/ejreidelbach/projects/NFL/Data/PlayerStats/' + position + '.csv'
df.to_csv(filename, index = False)