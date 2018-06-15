#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 16:16:17 2018

@author: ejreidelbach

:DESCRIPTION:
    This script will ingest the data for a position (right now it's focused
    on Wide Receiver data) and then calculate the similarity score between
    every player across all possible season groups.  By season groups, we're 
    referring to how many years of experience a player has in a given season.  
    So, all rookies are compared to each other while all 9th year veterans
    are compared to each other.  This is done regardless of when these seasons
    occurred, so a player's rookie season that happened in 2017 will be
    compared to all other rookie seasons regardless of year (i.e. 1998, 2003,
    etc.).
    
:REQUIRES:
    - Pandas
    - Numpy
   
:TODO:
    - functionalize the ability to specify what stats are desired for that
        specific computational run
    - specify default statistics fore each position
    - consider weighting variables and/or weighting different seasons
        (i.e. as you get older an the sample size decreases, lower the weight?)
"""
 
#==============================================================================
# Package Import
#==============================================================================
import math
import os  
import pandas as pd
from pathlib import Path
import numpy as np
import statistics

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
def calculate_agg_historical_values_by_exp(playersDF, stats_list):
    '''
    Description:
        This function will calculate the standard deviation and mean of every
        statistic across all possible years of experience in the position 
        data (i.e. 0, 1, 2, ..., 7, 8, 9, etc.).  This data will then be 
        utilized to calclate the "DEVIANCE" for each player in a separate 
        function.
    
    Input:
        playersDF (dataframe) - contains all player information and statistical
            information
        
    Output:
        historicalDict (dictionary) - Contains mean and standard deviation of 
            every statistic for every age group in the data. Results are stored 
            in separate sub-dictionaries:  
                * historicalStdDict: contains standard deviation data for 
                    each stat
                * historicalMeanDict: contains mean data for each stat
    '''    
    playersDF = df
    histDict = {}
    histStdDict = {}
    histMeanDict = {}
    
    # Iterate over every year of experience group in the positions data
    for yrs in playersDF['years_exp'].value_counts().sort_index().index.tolist():
        yearDF = playersDF[playersDF['years_exp'] == yrs].reset_index(drop=True)
        
        yrsStdDict = {}
        yrsMeanDict = {}
        for stat in stats_list:
            # Determine the standard deviation for the stat across all players
            yrsStdDict[stat] = yearDF[stat].std()
            yrsMeanDict[stat] = yearDF[stat].mean()
        histStdDict[str(yrs)] = yrsStdDict
        histMeanDict[str(yrs)] = yrsMeanDict
        print('Done with std and mean for years_exp: ' + str(yrs))
        
    # Store the calculated mean and standard deviation in a master dict
    #   called: `historicalDict`
    histDict['std'] = histStdDict
    histDict['mean'] = histMeanDict
    return histDict

def calculate_player_deviations_by_exp(playersDF, histDict, stats_list):
    '''
    Description:
        This function will take historical mean and standard deviation data
            for all player statistics across all years and calculate the 
            difference in standard deviations between a specific player (at 
            a specific number of years of experience) and all historical 
            players for every statistic.
            
        The number is then squared, multiplied by the proportion of a 
            predetermined weight assigned to that statistic (TBD). The square
            root of the sum of squares is then calculated to determine the
            "DEVIANCE."  By comparing deviances for each player, similar
            players can subsequently be identified.
    
    Input:
        playersDF (dataframe) - contains all player information and statistical
            information
        histDict (dictionary) - Contains mean and standard deviation of every
            statistic for every "years of experience" group in the data. 
            Results are stored in separate sub-dictionaries:  
                * historicalStdDict: contains standard deviation data for 
                    each stat
                * historicalMeanDict: contains mean data for each stat
        
    Output: 
        devianceList (list) - contains deviance values for every player
            for every "years of experience" of their playing career
    '''       
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
    #   difference between the player's stat and the group's mean.
    #   Divide that value standard deviations between the current player 
    #   and all historical players for each stat.
    # Then square the number, multiply it by the proportion of the weight 
    #   assigned to the category (TBD) and take the square root of the sum
    #   of squares.  This will be called the player's "DEVIANCE."
    for player in playersList:
        player_list = []
        for season in player:
            playerDict = {}
            playerDict['url'] = season['url']
            playerDict['years_exp'] = season['years_exp']
            for stat in stats_list:
                if np.isnan(season[stat]) or np.isnan(
                        histDict['std'][str(season['years_exp'])][stat]):
                    playerDict[stat] = float('nan')
                else:
                    diff = (season[stat] - histDict['mean'][str(
                            season['years_exp'])][stat])
                    if diff == 0:
                        playerDict[stat] = 0
                    else:
                        playerDict[stat] = diff / histDict['std'][str(
                            season['years_exp'])][stat]
            player_list.append(playerDict)
        devianceList.append(player_list)
        if playersList.index(player) % 100 == 0:
            print('Done calculating deviations for deviations for ' +
                  str(playersList.index(player)) + ' players')
    
    return devianceList

def calculate_similarity_scores_by_exp(devianceList, position, folder):
    '''
    Description:
        This function will take deviance scores between every player in a
            position group, across all seasons of a player's career, 
            and condense them to one score (computed as the median/mean of 
            all scores between two players across all played seasons
            they have in common)
        Note:  The term season, in this case, refers to years of experience
            (i.e. 4 seasons for a player = 4 years of experience). As such,
            seasons will start at 0 (rookie year) and work their way up over
            the span of a player's career (0, 1, 2, 3 ... 8, 9, 10).  Thus,
            the second year of a player's career would have an "experience" 
            value of 1 while the 11th year of a player's career would result
            in an experience value of 10
    
    Input:
        devianceList (list) - contains deviance values for every player
            for every age of their playing caree
        position (string) - string which contains the position group
            for the data being procssed
        folder (string) - string representation of Path where file should be
            output
        
    Output: 
       finalDF_median (dataframe) - contains deviance between every player in 
           the position group calculated by using the median of all shared
           deviance scores between the two players across their careers
    '''      
    # unpack list
    unpacked_list = []
    for player in devianceList:
        for season in player:
            unpacked_list.append(season)
    
    # put the data in a DataFrame to make age extraction simpler
    devianceDF = pd.DataFrame(unpacked_list)
    
    # for every age group, start calculating similarity scores between players
    # scores for each player will be stored in age groups
    deviance_dict_year = {}
    for yrs in devianceDF['years_exp'].value_counts().sort_index().index.tolist():
        year_list = devianceDF[devianceDF['years_exp'] == yrs].reset_index(
                drop=True).to_dict(orient='records')
        
        key_list = list(year_list[0].keys())
        deviance_dict_player = {}
        for player in year_list:
            deviance_dict_comp = {}
            for player2 in year_list:
                deviance = 0
                for key in key_list:
                    if key == 'yrs_exp' or key == 'url':
                        continue
                    elif math.isnan(player[key]) or math.isnan(player2[key]):
                        continue
                    deviance = deviance + (player[key] - player2[key])**2
                deviance_dict_comp[player2['url']] = (100-deviance)
            deviance_dict_player[player['url']] = deviance_dict_comp
        deviance_dict_year[str(yrs)] = deviance_dict_player
        print('Done with computing scores for years_exp: ' + str(yrs))
        
    # loop over all age groups and begin grouping scores by player instead
    # for every player, loop over every age he played and collect their scores
    url_list = devianceDF['url'].value_counts().sort_index().index.tolist()
    similarity_scores_dict = {}
    # step through every player in the data using their url as an identifier
    for url in url_list:
        #player_scores_list = []
        sim_dict = {}
        
        # iterate through every years of experience group (i.e. 0, 1, 2, etc.)
        for yearGroup in deviance_dict_year.keys():     
            
            # if the player exists in the year group, grab their similarity
            #   scores for every other player in that age group
            if url in deviance_dict_year[yearGroup].keys():
                sim_dict[yearGroup] = deviance_dict_year[yearGroup][url]
        similarity_scores_dict[url] = sim_dict
        if url_list.index(url)%100 == 0:
            print('Done collating scores for ' + 
                  str(url_list.index(url)) + ' players')                
                    
    # collapse the data such that each player has a link to every other player
    #   along with their respective deviance scores for every playing age/year
    #   they have in common
    # iterate across every player
    scores_dict = {}
    for player in similarity_scores_dict.keys():
        comparison_dict = {}
        # iterate across every year the player played
        for year in similarity_scores_dict[player].keys():
            # iterate across every player that has a similarity score
            for key, value in similarity_scores_dict[player][year].items():
                # don't include player's scores with self
                if key == player:
                    continue
                # if the player already exists in the dictionary, add the score
                elif key in comparison_dict.keys():
                    if comparison_dict[key] is not None:
                        tmp_list = comparison_dict[key]
                        tmp_list.append(value)
                        comparison_dict[key] = tmp_list
                # otherwise add them to the dictionary, then add the score
                else:
                    tmp_list = []
                    tmp_list.append(value)
                    comparison_dict[key] = tmp_list
        scores_dict[player] = comparison_dict
        if list(similarity_scores_dict.keys()).index(player)%100 == 0:
            print('Done collapsing scores for ' + 
                  str(list(similarity_scores_dict.keys()).index(
                          player)) + ' players')
        
    # average the scores of all lists in the scores_dict and output as a Dict
    final_dict = {}
    # iterate across every player
    for player in scores_dict.keys():
        comparison_dict = {}
        # iterate across every comaprison player for that player
        for key, value in scores_dict[player].items():
            player_dict = {}
            # extract the score list for that player and computer mean/median
            score_mean = statistics.mean(value)
            score_median = statistics.median(value)
            player_dict['mean'] = score_mean
            player_dict['median'] = score_median
            comparison_dict[key] = player_dict
        final_dict[player] = comparison_dict
        if list(scores_dict.keys()).index(player)%100 == 0:
            print('Done averaging scores for ' + 
                  str(list(scores_dict.keys()).index(
                          player)) + ' players')
    
    # convert the final stats into one dataframe
        
     # average the scores of all lists in the scores_dict and output as a DF
    final_dict_mean = {}
    final_dict_median = {}
    # iterate across every player
    for player in scores_dict.keys():
        player_dict_mean = {}
        player_dict_median = {}
        # iterate across every comaprison player for that player
        for key, value in scores_dict[player].items():

            # extract the score list for that player and computer mean/median
            player_dict_mean[key] = statistics.mean(value)
            player_dict_median[key] = statistics.median(value)
            
        final_dict_mean[player] = player_dict_mean
        final_dict_median[player] = player_dict_median
        if list(scores_dict.keys()).index(player)%100 == 0:
            print('Done averaging scores for ' + 
                  str(list(scores_dict.keys()).index(
                          player)) + ' players')
            
    finalDF_mean = pd.DataFrame(final_dict_mean)
    finalDF_mean.to_csv(Path(folder, 
                             position + '_exp_similarity_scores_mean.csv'))
    finalDF_median = pd.DataFrame(final_dict_median)
    finalDF_median.to_csv(Path(folder, 
                               position + '_exp_similarity_scores_median.csv'))
    return finalDF_median

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL')

# Iterate over every position folder
position_folder_list = [f.path for f in os.scandir(Path(
                                        'Data','PlayerStats')) if f.is_dir()]
for folder in position_folder_list:
    position = folder.split('Data/PlayerStats/')[-1]
    filename = Path(folder, position + '.csv')

    # Specify dtypes for specific columns that will give warnings without it
    df = pd.read_csv(filename, dtype = {
            'team_pic_url': str, 'high_school_state':str})
    
    # Identify the columns we want to fill in missing values for and replace 
    #   them with 0's
    stats_list = []
    cols_list = list(df.columns)
    for col in cols_list:
        if col.startswith('fumbles'):
            stats_list.append(col)
        elif col.startswith('kick_return'):
            stats_list.append(col)
        elif col.startswith('punt_return'):
            stats_list.append(col)
        elif col.startswith('receiving'):
            stats_list.append(col)
        elif col.startswith('rushing'):
            stats_list.append(col)
    for stat in stats_list:
        df.fillna({stat:0}, inplace=True)
    
    # Identify the stats we want to use for comparison purposes
    stats_list = []
    cols_list = list(df.columns)
    for col in cols_list:
        if col.startswith('combine') and (
                col not in ['combine_url', 'combine_draftYear']):
            stats_list.append(col)
        elif col in ['receiving_g',
                'receiving_rec',
                'receiving_yds',
                'receiving_td',
                'receiving_20+',
                'receiving_40+',
                'receiving_1st',
                'receiving_fum']:
            stats_list.append(col)
    
    # Calculate mean and standard deviation for all stats across all years
    historicDict = calculate_agg_historical_values_by_exp(df, stats_list)
    
    # Calculate the "deviance" for each player across every year on record
    devianceList = calculate_player_deviations_by_exp(df, historicDict, stats_list)    
    
    # Roll up all deviance scores, by years of experience,
    #   between all players into one final dictionary
    devianceDict = calculate_similarity_scores_by_exp(devianceList, position, folder)    