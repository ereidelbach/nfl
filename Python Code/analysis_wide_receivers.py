#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 29 08:30:17 2018

@author: ejreidelbach

:DESCRIPTION:

:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import os  
import pandas as pd

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
def calculate_historical_values(playersDF):
    historicalDict = {}
    historicalStdDict = {}
    historicalMeanDict = {}
    
    # Iterate over every age group in the positions data
    for age in playersDF['age'].value_counts().sort_index().index.tolist():
        #age = 23
        yearDF = playersDF[playersDF['age'] == age].reset_index()
        
        # Within each age group, calculate the difference in standard deviations
        #   between the current player and all historical players for each stat.
        # Then square the number, multiply it by the proportion of the weight 
        #   assigned to the category (TBD) and take the square root of the sum
        #   of squares.  This will be called the player's "DEVIANCE."
        ageStdDict = {}
        ageMeanDict = {}
        for stat in comp_list:
            # Determine the standard deviation for the stat across all players
            ageStdDict[stat] = yearDF[stat].std()
            ageMeanDict[stat] = yearDF[stat].mean()
        historicalStdDict[str(age)] = ageStdDict
        historicalMeanDict[str(age)] = ageMeanDict
        print('Done with age: ' + str(age))
        
    # Store the calculated mean and standard deviation in a master dict
    #   called: `historicalDict`
    historicalDict['std'] = historicalStdDict
    historicalDict['mean'] = historicalMeanDict
    return historicalDict

def calculate_player_deviations(playerDF, historicalDict):
    
#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/PlayerStats')

# Import the WR Data
df = pd.read_csv('WIDE_RECEIVER.csv')

# Determine the number of null values in our data
null_list = list(df.isnull().sum())
cols_list = list(df.columns)
null_dict = dict(zip(cols_list, null_list))

# Identify the stats we want to use for comparison purposes
comp_list = []
for col in cols_list:
    if col.startswith('fumbles'):
        comp_list.append(col)
    if col.startswith('kick_return'):
        comp_list.append(col)
    if col.startswith('punt_return'):
        comp_list.append(col)
    if col.startswith('receiving'):
        comp_list.append(col)
    if col.startswith('rushing'):
        comp_list.append(col)
  
historicDict = compare_player(df)

# Create aggregate player data based on their average season totals and their
#   median season totals
#df_mean = df.groupby(['url'], as_index = False).mean()
#df_median = df.groupby(['url'], as_index = False).median()
#
#var_list = [x for x in list(df.columns) if x not in list(df_mean.columns)]
#var_list.append('url')
#var_list.remove('team')
#
#df_mean_merge = pd.merge(df_mean, df[var_list], on=['url'], how='left')
#df_mean_merge.drop_duplicates(inplace=True)
#
#df_median_merge = pd.merge(df_median, df[var_list], on=['url'], how='left')
#df_median_merge.drop_duplicates(inplace=True)


    

    
    