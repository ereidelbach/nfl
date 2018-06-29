#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 15:32:48 2018

@author: ejreidelbach

:DESCRIPTION: This script converts the contents of a position file to a web
    friendly version usable by the current iteration of the React UI on 
    bit-bucket: https://bitbucket.org/wspencer428/prospect-vision/src

    The desired format is:
        [
          {
            id: 1,
            stats: [
                     {..stat objects..}
            ]
          }
          {
            id: 2,
            stats: [
                     {..stat objects..}
            ]
          }
        ]

:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import json
import os
import pandas as pd
from pathlib import Path

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================

#==============================================================================
# Working Code
#==============================================================================
          
# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/')

# Iterate over every position folder
position_folder_list = [f for f in os.listdir(Path('Data','PlayerStats'))]
for position in position_folder_list:
    # Identify the `position`.json files in the position folder
    path_position = Path('Data','PlayerStats',position)
    files = [str(Path(path_position,f)) for f in os.listdir(
            Path('Data','PlayerStats',position)) if f == (position+'.json')]
    files = sorted(files)
    
    # Read in all player data from the available JSON files into a list
    stat_list = []
    for file in files:
        with open(file, 'r') as f:
            jsonFile = json.load(f)   
            for player in jsonFile:
                stat_list.append(player)
                
    # create a dataframe from the list
    df = pd.DataFrame(stat_list)
    df_player = df[df['url'] == 'http://www.nfl.com/players/a.j.green/profile?id=GRE034604']
    df_player_dict = df_player.to_dict(orient='records')
                
#    # reconstruct the list into a list of dictionaries
#    # the dictionary will have two components:
#    #   - id: unique id for the player
#    #   - stats: stats for a player in a given season (as tuples)
#    player_list = []
#    for season in stat_list:
#        player_year_dict = {}
#        player_year_dict['id'] = stat_list.index(season)
#        player_year_dict['stats'] = season.items()
#        player_list.append(player_year_dict)
        
    # reconstruct the list into a list of dictionaries
    # the dictionary will have two components:
    #   - id: unique id for the player
    #   - stats: stats for a player in a given season (as a dictionary)
    player_list = []
    player_url = ''
    player_count = 0
    player_dict = {}
    season_list = []
    for season in stat_list:
        # if this is a new player, add the old player to the list and start
        #   a new player dictionary
        if player_url != season['url']:
            # check to make sure it's not the very first row before adding
            #   the player to the dictionary
            if stat_list.index(season) != 0:
                player_list.append(player_dict)
            # iterate the player count because it's a new player
            player_count+=1
            # update the player_url to match the new player
            player_url = season['url']
            # create a dictionary for the new player
            player_dict = {}
            player_dict['id'] = player_count
            # create a list for storing all the player data
            season_list = []
        # add the season to the player list
        season_list.append(season)
        # update the player's stats to include everything that's in the current
        #   version of the season list
        player_dict['stats'] = season_list
        # if it's the end of our list, add the player dict to the master list
        if stat_list.index(season) == (len(stat_list)-1):
            player_list.append(player_dict)
                
    # write the updated file to a new json file
    filename = position + '_web.json'
    with open(str(Path(path_position, filename)), 'wt') as out:
        json.dump(player_list, out, sort_keys=True, 
                  indent=4, separators=(',', ': '))