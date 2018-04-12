#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 10:03:18 2018

@author: ejreidelbach

:DESCRIPTION:
    - This script will transfer the individual player statistics contained in 
    the PFF 2018 NFL Draft Guide PDF into a .JSON file.
    
:REQUIRES:
    - Tabula  (https://pypi.python.org/pypi/tabula-py)
   
:TODO:
    - the information for G Will Hernandez is incorrect on page 172 and will 
    require manual correction in the output JSON file
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

# Code lifted from http://code.activestate.com/recipes/577279-generate-list-of-numbers-from-hyphenated-and-comma/
'''
    This function takes a range in form of "a-b" and generate a list of numbers 
    between a and b inclusive. Also accepts comma separated ranges like 
    "a-b,c-d,f" will build a list which will include numbers from a to b, 
    a to d and f Example: hyphen_range('54-78') hyphen_range('57-78,454,45,1-10') 
    hyphen_range('94-100,1052,2-50')
'''
def hyphen_range(s):
    """ Takes a range in form of "a-b" and generate a list of numbers between a and b inclusive.
    Also accepts comma separated ranges like "a-b,c-d,f" will build a list which will include
    Numbers from a to b, a to d and f"""
    s="".join(s.split())#removes white space
    r=set()
    for x in s.split(','):
        t=x.split('-')
        if len(t) not in [1,2]: raise SyntaxError("hash_range is given its arguement as "+s+
              " which seems not correctly formated.")
        r.add(int(t[0])) if len(t)==1 else r.update(set(range(int(t[0]),int(t[1])+1)))
    l=list(r)
    l.sort()
    return l

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

for position in playerPageDict:
    # Update me as to where we are in the loop
    print("Starting " + position)
    
    # Extract each player page in the position
    playerNameList = []
    playerInfoList = []
    playerStatsList = []
    advStatsList = []
    page_nums = hyphen_range(playerPageDict[position])
    for num in page_nums:
        # area format is y1,x1,y2,x2
        playerNameList.append(read_pdf('2018 Draft Guide v2.pdf', 
                                        pages=num,
                                        stream=True,
                                        area = "31.185,34.155,69.795,300",
                                        guess=False,
                                        pandas_options={'header':None}))
        playerInfoList.append(read_pdf('2018 Draft Guide v2.pdf', 
                                        pages=num,
                                        area = "69.795,29.205,120.335,313.335",
                                        guess=False,
                                        pandas_options={'header':None}))
        playerStatsList.append(read_pdf('2018 Draft Guide v2.pdf', 
                                        pages=num,
                                        area = "109.395,26.73,198.495,391.05",
                                        guess=False))
        advStatsList.append(read_pdf('2018 Draft Guide v2.pdf',
                                     pages=num,
                                     area = "372.735,381.15,587.565,579.15",
                                     guess=False))
        print("Extracted " + str(position) + " #" + str(num) + 
              " NameSize=" + str(playerNameList[-1].shape) + " InfoSize=" +
              str(playerInfoList[-1].shape) + " StatsSize=" + 
              str(playerStatsList[-1].shape) + " advStatsSize=" + 
              str(advStatsList[-1].shape))
        
    # Merge tables containing player information into one JSON file
    playerList = []
    for count in range(0,len(page_nums)):
        playerInfo = {}
        # Name and Position        
        playerInfo['position'] = playerNameList[count].loc[0,0].split(' ')[0]
        playerInfo['nameFirst'] = playerNameList[count].loc[0,0].split(' ')[1]
        playerInfo['nameLast'] = playerNameList[count].loc[0,0].split(' ' )[2]
        
        # Basic Player Info
        playerInfo['TEAM'] = playerInfoList[count].loc[0,0].split(': ')[1]
        playerInfo['schoolYear'] = playerInfoList[count].loc[0,1].split(': ')[1]
        playerInfo['pffGrade'] = playerInfoList[count].loc[1,0].split(': ')[1]
        playerInfo['pffPosRank'] = playerInfoList[count].loc[1,1].split(': ')[1]
        
        # Player Historic Stats
        stats = []
        stats = playerStatsList[count].to_dict('records')
        for item in stats:
            year = item.pop('Unnamed: 0')
            if (year == 'THREE YEAR STATS'):
                year = 'ThreeYearTotal'
            year = 'stats'+str(year)
            # recast stats as strings to avoid the following error:
            #   Object of type 'int64' is not JSON serializable
            item = {k:str(v) for k, v in item.items()}
            playerInfo[year] = item
                            
        # Player Advanced Stats
        advStats = advStatsList[count].T.iloc[:2,:]
        advStats.columns = advStats.iloc[0,:]
        advStats.drop(advStats.index[0], inplace=True)
        playerInfo.update(advStats.to_dict('records')[0])
        playerList.append(playerInfo)
    
    # Output the list to a file
    fname_new = 'pff_draft_guide_2018_player_statistics_' + str(position) + '.json'
    with open(fname_new, 'wt') as out:
        json.dump(playerList, out, sort_keys=True, indent=4, separators=(',', ': '))