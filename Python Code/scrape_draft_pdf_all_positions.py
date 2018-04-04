#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 13:07:16 2018

@author: ejreidelbach

:DESCRIPTION:
    - This script will transfer the contents of the PFF 2018 NFL Draft Guide PDF
    into a .JSON file.

:REQUIRES:  
    - Tabula  (https://pypi.python.org/pypi/tabula-py)
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import os  
from tabula import read_pdf
import pandas as pd
import json

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
statsList = []

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/Draft')

# Helpful Tutorials
# https://medium.com/dunder-data/selecting-subsets-of-data-in-pandas-6fcd0170be9c
# https://dbsnail.com/2017/11/07/extracting-tables-in-pdf-format-with-tabula-py/
# https://blog.chezo.uno/tabula-py-extract-table-from-pdf-into-python-dataframe-6c7acfa5f302

# Extract PFF Position Rankings
rankingPageDict = {'QB':5, 'RB':26, 'WR':47, 'TE':87, 'OT':103, 'OG':125,
                   'OC':142, 'CB':156, 'S':184, 'LB':208, 'DT':242, 'DE':274}

#df2 = read_pdf('draft-guide2018.pdf',pages=rankingPageDict['QB'])

# Extract the PFF Positional Statistics
statsPageDict = {'QB:Adjusted_Completion_Percentage':'6-7',
                 'QB:Under_Pressure':'8-9',
                 'QB:Deep_Passing':'10-11',
                 'RB:Elusive_Rating':'28-29',
                 'RB:Pass_Blocking_Efficiency':'30-31',
                 'WR:Yards_Per_Route_Run':'49-52',
                 'WR:Deep_Passing':'53-55',
                 'WR:Drop_Rate':'56-59',
                 'WR:Slot_Performance':'60-61',
                 'TE:Yards_Per_Route_Run':'89-90',
                 'OT:Pass_Blocking_Efficiency':'105-107',
                 'OG:Pass_Blocking_Efficiency':'127-128',
                 'OC:Pass_Blocking_Efficiency':'144-145',
                 'CB:Coverage':'158-161',
                 'CB:Slot_Performance':'162-164',
                 'S:Run_Stop_Percentage':'186-188',
                 'S:Tackling_Efficiency':'189-192', #requires special handling
                 'LB:Run_Stop_Percentage':'210-213',
                 'LB:Tackling_Efficiency':'214-217', #requires special handling
                 'LB:Pass_Rush_Opportunity':'218-221',
                 'DT:Pass_Rush_Productivity':'244-248',
                 'DT:Run_Stop_Percentage':'249-253',
                 'DE:Pass_Rush_Productivity':'276-279', #requires special handling
                 'DE:Run_Stop_Percentage':'280-283'}

for key in statsPageDict:
    # Update me as to where we are in the loop
    print("Starting " + key)
    
    # Grab the requested tables from the specified PDF pages
    tempStats = read_pdf('draft-guide2018.pdf', multiple_tables = True,
              pages=statsPageDict[key])
    
    # Extract the information from the retrieved tables
    # Skip the first row of each table to ignore the column headers
    storageDF = pd.DataFrame(data=None, columns=tempStats[0].columns)
    tempList = []
    for tables in tempStats:
        tempDF = tables.loc[1:,]
        tempDF = tempDF.dropna(axis=1, how='all')
        tempDF.columns = range(tempDF.shape[1])
        tempList.append(tempDF)
        storageDF = pd.concat([storageDF,tempDF], ignore_index = True)
        storageDF = storageDF.dropna(axis=1, how='all')
    
    # Once we have all the information, grab the column headers
    # In certain cases, the column header format is different so we must account
    #   for that and delete unnecessary rows as required
    if key in (['S:Tackling_Efficiency','LB:Tackling_Efficiency']):
        storageDF.columns = ['NAME','TEAM','RUNNING: SNAPS',
                             'RUNNING: MISSED TACKLES',
                             'RUNNING: TACKLE EFFICIENCY',
                             'PASSIN: SNAPS','PASSING:MISSED TACKLES',
                             'PASSING: TACKLE EFFICIENCY',
                             'COMB. TACKLE EFFICIENCY']
        storageDF = storageDF[storageDF.NAME != 'NAME']
    elif key == 'DE:Pass_Rush_Productivity':
        storageDF.columns = ['NAME','TEAM','LEFT: PR SNAPS','LEFT: PRP',
                             'RIGHT: PR SNAPS','RIGHT: PRP','ALL: PASSING SNAPS',
                             'ALL: PASS RUSH %','ALL: SK','ALL: HT','ALL: HU',
                             'ALL: TOTAL PRESSURE','ALL:PRP']
        storageDF = storageDF[storageDF.NAME != 'NAME']
    else:    
        storageDF.columns = tables.loc[0,]
    
    # Split up the player name column into first_name and last_name columns
    storageDF['nameFirst'], storageDF['nameLast'] = storageDF['NAME'].str.split(' ', 1).str
    
    # The WR:Deep_Passing table has two columns named `Targets` ---> change the
    #   second of the columns to be named `DEEP TARGETS`
    if key == 'WR:Deep_Passing':
        storageDF.columns.values[3] = 'DEEP TARGETS'
    
    # Add the extracted information to a permanent list
    storageDict = storageDF.to_dict('records')
    for d in storageDict:
        statsList.append(d)

# Output the list to a file
fname_new = 'pff_draft_guide_2018_statistics_all_positions.json'
with open(fname_new, 'wt') as out:
    json.dump(statsList, out, sort_keys=True, indent=4, separators=(',', ': '))
