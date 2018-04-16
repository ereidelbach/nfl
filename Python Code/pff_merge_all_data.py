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
import csv
import json
import os  
import pandas as pd
from pandas.io.json import json_normalize

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
# Establish dictionary for standardizing school names
schoolAbbrevDict = {}
with open('/home/ejreidelbach/projects/NFL/Data/school_abbreviations.csv') as fin:
    reader=csv.reader(fin, skipinitialspace=True, quotechar="'")
    for row in reader:
        valueList = list(filter(None, row[1:]))
        schoolAbbrevDict[row[0]]=valueList
                   
#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/DraftV2/Temp')

# Iterate through each position and read in all files
posList = ['QB', 'RB', 'WR', 'TE', 'OT', 'OG', 'OC', 'CB', 'S', 'LB', 'DT', 'DE']
statsFile = r'/home/ejreidelbach/projects/NFL/Data/DraftV2/Temp/pff_draft_guide_2018_statistics_'
playerStatsFile = r'/home/ejreidelbach/projects/NFL/Data/DraftV2/Temp/pff_draft_guide_2018_player_statistics_'

masterList = []
for pos in posList:
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
    
    # The Team column in statsDF needs to be changed to match playerStatsDF
    for i in range(len(statsDF['TEAM'].values)):
        for school in schoolAbbrevDict:
            schoolList = [x.lower() for x in schoolAbbrevDict[school]]
            if statsDF['TEAM'].values[i].lower() in schoolList:
                statsDF['TEAM'].values[i] = school
            elif statsDF['TEAM'].values[i].lower() == school.lower():
                statsDF['TEAM'].values[i] = school      
    
    # We normalize the playerStats file to flatten the nested columsn for yearly data
    playerStatsDF = json_normalize(jsonPlayerStats)
    
    # Merge the two separate datasets into one cohesive dataframe
    #mergeDF = pd.merge(statsDF, playerStatsDF, how='outer')
    mergeDF = pd.merge(statsDF, playerStatsDF, on=['nameFirst','nameLast','TEAM'],
                       how='outer')
    
    # remove the original `NAME` column as we have nameFirst and nameLast columns
    mergeDF = mergeDF.drop('NAME', 1)
    
    # Convert the merged DataFrame to a list of dictionaries
    positionList = []
    positionDict = mergeDF.to_dict('records')
    for d in positionDict:
        positionList.append(d)    
        masterList.append(d)
    
    # Output the reduced merged list
    fname_pos = '/home/ejreidelbach/projects/NFL/Data/DraftV2/pff_draft_guide_2018_statistics_' + pos + '.json'
    with open(fname_pos, 'wt') as out:
        json.dump(positionList, out, sort_keys=True, indent=4, separators=(',', ': '))

# Output the combined file for all positions
fname_new = r'/home/ejreidelbach/projects/NFL/Data/DraftV2/pff_draft_guide_2018_statistics_Combined.json'
with open(fname_new, 'wt') as out:
    json.dump(masterList, out, sort_keys=True, indent=4, separators=(',', ': '))
