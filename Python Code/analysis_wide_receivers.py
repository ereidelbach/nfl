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
import math
import os  
import pandas as pd
import numpy as np

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
def calculate_agg_historical_values(playersDF, stats_list):
    '''
    Description:
        This function will calculate the standard deviation and mean of every
        statistic across every age group in the position data (i.e. age 22,
        23, 24...35, 36, 37, etc.).  This data will then be utilized to 
        calclate the "DEVIANCE" for each player in a separate function.
    
    Input:
        playersDF (dataframe) - contains all player information and statistical
            information
        
    Output:
        historicalDict (dictionary) - Contains mean and standard deviation of every
            statistic for every age group in the data. Results are stored in 
            separate sub-dictionaries:  
                * historicalStdDict: contains standard deviation data for 
                    each stat
                * historicalMeanDict: contains mean data for each stat
    '''    
    playersDF = df
    histDict = {}
    histStdDict = {}
    histMeanDict = {}
    
    # Iterate over every age group in the positions data
    for age in playersDF['age'].value_counts().sort_index().index.tolist():
        yearDF = playersDF[playersDF['age'] == age].reset_index()
        
        ageStdDict = {}
        ageMeanDict = {}
        for stat in stats_list:
            # Determine the standard deviation for the stat across all players
            ageStdDict[stat] = yearDF[stat].std()
            ageMeanDict[stat] = yearDF[stat].mean()
        histStdDict[str(age)] = ageStdDict
        histMeanDict[str(age)] = ageMeanDict
        print('Done with age: ' + str(age))
        
    # Store the calculated mean and standard deviation in a master dict
    #   called: `historicalDict`
    histDict['std'] = histStdDict
    histDict['mean'] = histMeanDict
    return histDict

def calculate_player_deviations(playersDF, histDict, stats_list):
    '''
    Description:
        This function will take historical mean and standard deviation data
            for all player statistics across all years and calculate the 
            difference in standard deviations between a specific player (at 
            a specific age) and all historical players for every statistic.
            
        The number is then squared, multiply by the proportion of a 
            predetermined weight assigned to that statistic (TBD). The square
            root of the sum of squares is then calculated to determine the
            "DEVIANCE."  By comparing deviances for each player, similar
            players can subsequently be identified.
    
    Input:
        playersDF (dataframe) - contains all player information and statistical
            information
        histDict (dictionary) - Contains mean and standard deviation of every
            statistic for every age group in the data. Results are stored in 
            separate sub-dictionaries:  
                * historicalStdDict: contains standard deviation data for 
                    each stat
                * historicalMeanDict: contains mean data for each stat
        
    Output: 
        devianceDict (dictionary) - contains deviance values for every player
            for every age of their playing career
    '''    
#    playersDF = df
#    histDict = historicDict
    
    # extract all the players in the dataframe
    playersList = []
    url_list = playersDF['url'].value_counts().sort_index().index.tolist()
    for url in url_list:
        tempDF = playersDF[playersDF['url'] == url]
        playersList.append(tempDF.to_dict(orient='records'))
    
    # create a list for storing all deviance scores
    #   each player will have a separate score for every year they've played
    devianceList = []
     
    # Iterate over every player in the playersDF
    # For each recorded year we have data on the player, calculate the 
    #   difference between the player's stat and the age group's mean.
    #   Divide that value standard deviations between the current player 
    #   and all historical players for each stat.
    # Then square the number, multiply it by the proportion of the weight 
    #   assigned to the category (TBD) and take the square root of the sum
    #   of squares.  This will be called the player's "DEVIANCE."
    for player in playersList:
        player_list = []
        for season in player:
            playerDict = {}
#            playerDict['url'] = season['url']
            playerDict['age'] = season['age']
            for stat in stats_list:
                if np.isnan(season[stat]) or np.isnan(
                        histDict['std'][str(season['age'])][stat]):
                    playerDict[stat] = float('nan')
                else:
                    diff = (season[stat] - histDict['mean'][str(
                            season['age'])][stat])
                    if diff == 0:
                        playerDict[stat] = 0
                    else:
                        playerDict[stat] = diff / histDict['std'][str(
                            season['age'])][stat]
            player_list.append(playerDict)
        devianceList.append(player_list)
    
    return devianceList
        
#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/PlayerStats')

# Specify dtypes for specific columns that will give warnings without it
types = {'team_pic_url': str, 'high_school_state':str}
# Import the WR Data
df = pd.read_csv('WIDE_RECEIVER.csv', dtype = types)

# Identify the stats we want to use for comparison purposes
stats_list = []
cols_list = list(df.columns)
for col in cols_list:
    if col.startswith('combine') and col != 'combine_url':
        stats_list.append(col)
#    if col.startswith('fumbles'):
#        stats_list.append(col)
#    if col.startswith('kick_return'):
#        stats_list.append(col)
#    if col.startswith('punt_return'):
#        stats_list.append(col)
    if col.startswith('receiving'):
        stats_list.append(col)
#    if col.startswith('rushing'):
#        stats_list.append(col)

# Calculate mean and standard deviation for all stats across all years
historicDict = calculate_agg_historical_values(df, stats_list)

# Calculate the "deviance" for each player across every year on record
devianceDict = calculate_player_deviations(df, historicDict, stats_list)

    
    