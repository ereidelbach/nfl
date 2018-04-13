#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 11:39:37 2018

@author: ejreidelbach

:DESCRIPTION:
    - ingest PFF data for players, by position, from statistics_POS and
        player_statistics_POS
    - data will contain basic player information, historic statistics, and
        PFF specific statistics
    - data will be merged into one cohesive listing of all relevant player data
        for each position

:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import json
import os  
import pandas as pd
from pandas.io.json import json_normalize

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/DraftV2/Temp')

# Iterate through each position and read in all files
posList = ['QB', 'RB', 'WR', 'TE', 'OT', 'OG', 'OC', 'CB', 'S', 'LB', 'DT', 'DE']
statsFile = r'/home/ejreidelbach/projects/NFL/Data/DraftV2/Temp/pff_draft_guide_2018_statistics_'
playerStatsFile = r'/home/ejreidelbach/projects/NFL/Data/DraftV2/Temp/pff_draft_guide_2018_player_statistics_'

for pos in posList:
    pos = 'DE'
    print("Reading in " + str(pos))
    file1 = statsFile + str(pos) + '.json'
    print(file1)
    file2 = playerStatsFile + str(pos) + '.json'
    print(file2)

    # Read in JSON of regular stats
    with open(file1, 'r') as json_data:
        jsonStats = json.load(json_data)
    # Read in JSON of other player stats
    with open(file2, 'r') as json_data:
        jsonPlayerStats = json.load(json_data)

    # Some keys are the same but they are spelled slighty different due to
    # formatting errors in the source document.
    #  Let's fix this:
    for dictionary in jsonPlayerStats:
        for oldKey in dictionary:
            if 'PRODUCIVITY' in oldKey:
                newKey = oldKey.replace('PRODUCIVITY','PRODUCTIVITY')
                newKey = newKey.replace('-',' ').strip()
            else:
                newKey = oldKey.replace('-',' ').strip()
            dictionary[newKey] = dictionary.pop(oldKey)
        
    # Convert JSON files to Pandas DataFrames
    statsDF = pd.DataFrame.from_records(jsonStats)
    # The Team column needs to be converted to upper case to match the same 
    #   column in playerStatsDF
    statsDF['TEAM'] = statsDF['TEAM'].str.upper()
    
    # We normalize the playerStats file to flatten the nested columsn for yearly data
    playerStatsDF = json_normalize(jsonPlayerStats)
    
    # Merge the two separate datasets into one cohesive dataframe
    mergeDF = pd.merge(statsDF, playerStatsDF, how='outer')
           
    # Output the reduced json file
    fname_new = r'/home/ejreidelbach/projects/NFL/Data/DraftV2/Temp/pff_draft_guide_2018_statistics_Combined.json'
    with open(fname_new, 'wt') as out:
        json.dump(masterPosList, out, sort_keys=True, indent=4, separators=(',', ': '))