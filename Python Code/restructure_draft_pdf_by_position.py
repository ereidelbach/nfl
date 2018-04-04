#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 16:23:39 2018

@author: ejreidelbach

:DESCRIPTION:
    - This script will merge the multiple .json files in the Draft folder for 
    each position into one file per position
    - i.e. `pff_draft_guide_2018_statistics_CB` instead of:
        * pff_draft_guide_2018_statistics_CB:Coverage   -AND-
        * pff_draft_guide_2018_statistics_CB:Slot_Performance

:REQUIRES:
   
:TODO:
    - position data is not merging correctly 
    - suspect columns have similar names across multiple files and that they
        are overwriting one another
"""
 
#==============================================================================
# Package Import
#==============================================================================
import json
import os  
import pandas as pd

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/Draft/Positional')

# Read in all Files
files = [f for f in os.listdir('.') if f.endswith(('.json'))]
files = sorted(files)

# Break up files into position groups for processing
fileDict = {}
for f in files:
    pos = f.split('_statistics_')[1].split(':')[0]
    if pos not in fileDict.keys():
        fileDict[pos] = [f.split('_statistics_')[1].split(':')[1].split('.json')[0]]
    else:
        fileDict[pos].append(f.split('_statistics_')[1].split(':')[1].split('.json')[0])

# Read in JSON file as JSON object
for posDict in fileDict:
    positionDF = pd.DataFrame()
    posFiles = fileDict[posDict]
    for stats in posFiles:
        f = 'pff_draft_guide_2018_statistics_' + str(posDict) + ':' + str(stats) + '.json'
        print("Reading in " + str(posDict) + ':' + str(stats) + '.json')
        with open(f, 'r') as json_data:
            jsonFile = json.load(json_data)
        
        # Read in JSON file as Pandas DataFrame
        tempDF = pd.DataFrame.from_records(jsonFile)
        positionDF = pd.concat([positionDF,tempDF], ignore_index = True)
        
        # Convert DF to a list of dictionaries
        positionList = []
        positionDict = positionDF.to_dict('records')
        for d in positionDict:
            positionList.append(d)
            
        # Output the reduced json file
        fname_new = r'/home/ejreidelbach/projects/NFL/Data/Draft/pff_draft_guide_2018_statistics_' + str(posDict) + '.json'
        with open(fname_new, 'wt') as out:
            json.dump(positionList, out, sort_keys=True, indent=4, separators=(',', ': '))