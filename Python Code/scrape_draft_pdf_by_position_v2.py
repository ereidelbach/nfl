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

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/DraftV2')

# Helpful Tutorials
# https://medium.com/dunder-data/selecting-subsets-of-data-in-pandas-6fcd0170be9c
# https://dbsnail.com/2017/11/07/extracting-tables-in-pdf-format-with-tabula-py/
# https://blog.chezo.uno/tabula-py-extract-table-from-pdf-into-python-dataframe-6c7acfa5f302

# Extract PFF Position Rankings
playerPageDict = {'QB':'13-27', 'RB':'39-59', 'WR':'81-108', 'TE':'125-131', 
                  'OT':'144-157', 'OG':'171-177', 'OC':'193-201', 'CB':'334-359', 
                  'S':'381-396', 'LB':'297-315', 'DT':'256-272', 'DE':'215-235'}
playerMultiPageDict = {'QB':'28-32', 'RB':'60-65', 'WR':'109-120', 'TE':'132-138', 
                       'OT':'158-166', 'OG':'178-188', 'OC':'202-204', 'CB':'360-370',
                       'S':'397-408', 'LB':'316-325', 'DT':'273-282', 'DE':'236-243'}

# Extract the PFF Positional Statistics
statsPageDict = {'QB:Adjusted_Completion_Percentage':'7-8',
                 'QB:Under_Pressure':'9-10',
                 'QB:Deep_Passing':'11-12',
                 'RB:Elusive_Rating':'35-36',
                 'RB:Pass_Blocking_Efficiency':'37-38',
                 'WR:Yards_Per_Route_Run':'68-71',
                 'WR:Deep_Passing':'72-74',
                 'WR:Drop_Rate':'75-78',
                 'WR:Slot_Performance':'79-80',
                 'TE:Yards_Per_Route_Run':'123-124',
                 'OT:Pass_Blocking_Efficiency':'141-143',
                 'OG:Pass_Blocking_Efficiency':'169-170',
                 'OC:Pass_Blocking_Efficiency':'191-192',
                 'CB:Coverage':'328-331',
                 'CB:Slot_Performance':'332-333,371',
                 'S:Run_Stop_Percentage':'374-376',
                 'S:Tackling_Efficiency':'377-380', #requires special handling
                 'LB:Run_Stop_Percentage':'285-288',
                 'LB:Tackling_Efficiency':'289-292', #requires special handling
                 'LB:Pass_Rush_Opportunity':'293-296',
                 'DT:Pass_Rush_Productivity':'246-250',
                 'DT:Run_Stop_Percentage':'251-255',
                 'DE:Pass_Rush_Productivity':'207-210', #requires special handling
                 'DE:Run_Stop_Percentage':'211-214'}

for key in statsPageDict:
    statsList = []
    # Update me as to where we are in the loop
    print("Starting " + key)
    
    # Grab the requested tables from the specified PDF pages
    tempStats = read_pdf('2018 Draft Guide v2.pdf', multiple_tables = True,
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
    fname_new = 'Positional/pff_draft_guide_2018_statistics_' + str(key) + '.json'
    with open(fname_new, 'wt') as out:
        json.dump(statsList, out, sort_keys=True, indent=4, separators=(',', ': '))
