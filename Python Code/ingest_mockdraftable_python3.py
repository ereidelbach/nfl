#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 10:13:51 2018

@author: ejreidelbach

description

:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import os  
import pandas as pd
import json

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
varNames = ['nameFirst', 'nameLast', 'draftYear', 'college', 'heightFeet', 
            'heightInches','weight', 'wingspan', 'lengthArm', 'lengthHand', 
            'combine10split', 'combine20split', 'combine40dash', 'combineBench', 
            'combineVert', 'combineBroad', 'combineCone', 'combine20shuttle', 
            'combine60shuttle','url','position']
playerDict = {}

#==============================================================================
# Working Code
#==============================================================================

# JSON file
filename = r'Data/Combine/mockdraftable_data.json'

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL')

## There are duplicate entries for the QB position (Remove them and export JSON)
#df = df.drop_duplicates()
#jsonFileSmall = df.to_dict('records')
#
## Output the reduced json file
#fname_new = 'mockdraftable_data_reduced.json'
#with open(fname_new, 'wt') as out:
#    json.dump(jsonFileSmall, out, sort_keys=True, indent=4, separators=(',', ': ')) 

# Read in JSON file as JSON object
with open(filename, 'r') as f:
    jsonFile = json.load(f)

# Read in JSON file as Pandas DataFrame
df = pd.DataFrame.from_records(jsonFile)
    
# Extract just WRs and QBs for simplified analysis
jsonFileReduced = []
for player in jsonFile:
    if player['position'] in ['QB','WR']:
        jsonFileReduced.append(player)

# Output the reduced json file
fname_new = 'Data/Combine/mockdraftable_data_QB_WR.json'
with open(fname_new, 'wt') as out:
    json.dump(jsonFileReduced, out, sort_keys=True, indent=4, separators=(',', ': '))