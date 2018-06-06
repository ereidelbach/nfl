#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 24 12:54:49 2018

@author: ejreidelbach

:DESCRIPTION:
    - This script will read in scraped JSONs from NFL.com and flatten nested
        portions of those JSON files (the career and situational stats) which
        are currently stored in lists. This script will unpack those nested 
        lists and flatten them such that every variable is placed in its own
        column whereas every player will be in his own row.
    - This script will also correct any inaccuracies in draft-related info
        that is contained in player statistical data scraped from NFL.com.
    - The historic draft data was scraped from: http://www.drafthistory.com/

:REQUIRES:    
    - The script does not account for player's changing teams mid-year
        ** example page: http://www.nfl.com/player/kennybritt/71217/careerstats
        # Kenny changes teams in 2017 from New England to Cleveland but the 
            script treats the Cleveland line as 2016 and then duplicates the 
            2009 season with Tennessee twice.  
        # Need to correct this by grouping by year and combining to one line
        
    - When correcting for multiple teams in the same year, entries do not
        account for the calculations needed for stat categories such as
        Avg, Long, Pct, etc.. for positions other than Wide Receiver
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import itertools
import json
import pandas as pd
import os
import copy
from datetime import datetime
import math

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
# positions for which stats can be obtained
position_list = ['QUARTERBACK',
                 'RUNNING_BACK',
                 'WIDE_RECEIVER',
                 'TIGHT_END',
                 'DEFENSIVE_LINEMAN',
                 'LINEBACKER',
                 'DEFENSIVE_BACK',
                 'PUNTER',
                 'FIELD_GOAL_KICKER',
                 ]


def update_draft_info(player_list):
    '''
    Description:
        This function matches an NFL player with his respective draft info,
        if it exists, thus correcting any gaps in data obtained from NFL.com
    
    Input:
        player_list (list) - contains all scraped player info from NFL.com
        draft_list (list) - contains information on players drafted since 1970
        
    Output:
        final_list (list) - contains all player stat information along with
            updated draft information
    '''
    # read in the historic draft data
    with open(r'/home/ejreidelbach/projects/NFL/Data/Draft/historic_draft_data.json', 'r') as f:
        draft_list = json.load(f)

#    final_list = []

    # iterate over every player in the player list and update their information
    #   with information obtained from the draft_list
    for player in player_list:
        
#        # create a temporary dictionary for the purposes of slimming down the
#        #   data in a test environment
#        temp_dict = {k: player[k] for k in (
#                'name_first', 
#                'name_last',
#                'year',
#                'college',
#                'draft_pick_overall',
#                'draft_pick_round',
#                'draft_round',
#                'draft_team',)}
#        temp_dict['nameFirst'] = temp_dict.pop('name_first')
#        temp_dict['nameLast'] = temp_dict.pop('name_last')
#        temp_dict['school'] = temp_dict.pop('college')
#        temp_dict['overall'] = temp_dict.pop('draft_pick_overall')
#        temp_dict['round'] = temp_dict.pop('draft_round')
#        temp_dict['pick'] = temp_dict.pop('draft_pick_round')
#        temp_dict['team'] = temp_dict.pop('draft_team')

        # find a matching player in draft_list based on:
        #   player_list:  name_first, name_last, college
        #   draft_list:  nameFirst, nameLast, school
        # Once a player is found, extract their draft info and add it to
        #   the player's historic information and stop the for loop so that
        #   the next player can be updated
        for pick in draft_list:
            if (player['name_first'] == pick['nameFirst'] 
            and player['name_last'] == pick['nameLast'] 
            and player['college'].split(' ')[0] == pick['school'].split(' ')[0]):
#                for k, v in pick.items():
#                    key = k + '_historic'
#                    temp_dict[key] = v
#                final_list.append(temp_dict)
                player['draft_pick_overall'] = pick['overall']
                player['draft_pick_round'] = pick['pick']
                player['draft_round'] = pick['round']
                player['draft_team'] = pick['team']
                break
#        finalDF = pd.DataFrame(final_list)
#        finalDF['duplicated'] = finalDF.duplicated()
#        finalDF.drop_duplicates(inplace=True)
#        finalDF_filtered = finalDF[finalDF['team'] != finalDF['team_historic']]
    return player_list

def merge_combine_data(player_list):
    '''
    Description:
        This function will merge scraped player data from NFL.com with 
            combine data (if it exists) from mockdraftable.com
    
    Input:
        player_list (list) - contains all player info from NFL.com
            for a specific player
        
    Output:
        final_list (list) - contains all player information to include newly
            merged combine data from mockdraftable.com
    '''    

def combine_multiyear_stats(annual_list):
    '''
    Description:
        This function accounts for cases in which players play for multiple
        teams within the same season.  To account for this, all stats in the
        same season will be summed together to form singular values.  The
        player's team for that season will be whatever team they last played
        for in that season.
    
    Input:
        annual_list (list) - contains all career stat player info from NFL.com
            for a specific player
        
    Output:
        final_list (list) - contains all player stat information that has
            been compressed/rolled up such that there is only one record (row)
            per player per year
    '''
#   Edge case for checking data in multiple years
#   annual_list = stat_list[469]['stats_annual']
    annualDF = pd.DataFrame(annual_list)
    try:
        year_count = annualDF['year'].value_counts()
    except:
        return []
    
    # If there exists more than one row per year, combine the results of those
    #   rows such that there is only one row per year
    final_list = []
    for index, count in year_count.iteritems():
        if int(count) > 1:
            # extract the data for those rows
            years_dict = annualDF[annualDF['year'] == index].to_dict()
            
            # start combining the data for those rows in a new dict
            #   All stats can be summed together with the exception of the 
            #   following values:  
            #       Receiving: `Avg`, `Yds/G`, `Lng`
            #       Rushing: `Att/G`, `Avg`, `Yds/G`, `Lng`, `1st%`
            #       Returns: `Avg`, `Lng`
            #       Defensive: `Avg`, `Lng`
            #       Fumbles: ----
            #       Passing: `Pct`, `Att/G`, `Avg`, `Yds/G`, `TD%`, `Int%`, 
            #                `Lng`, `Rate`
            #       Punting: `Lng`, `Avg`, `Net Avg`
            #       Kickoff: `Avg`, `Pct`, `Avg`
            #       Field Goal: `Lng`, `Pct`, `Pct`, `Pct`, `Pct`, `Pct`, `Pct`
            temp_dict = {}

            for entry in years_dict:
                # Determine what stat category we're dealing with so we know
                #    what values to use for calculations
                if 'return' in entry:
                    category = '_'.join(entry.split('_')[0:2])
                else:
                    category = entry.split('_')[0]
                    
                # set variables names to be used for stat calculations
                att = ''              
                if 'return' in category:
                    att = category + '_ret'
                elif category == 'receiving': 
                    att = category + '_rec'
                elif category == 'rushing':
                    att = category + '_att'
                yds = category + '_yds'
                if category == 'punt_return':
                    yds = category + '_rety'
                g = category + '_g'
                first = category + '_1st'
                
                # special calculations are required for statistics that
                #   containt the values listed above.  They are calculated on
                #   a case by case basis:                    
                # avg = yds / att
                if 'avg' in entry:   
                    if sum(list(map(int, years_dict[att].values()))) == 0:
                        temp_dict[entry] = 0
                    else:
                        temp_dict[entry] = sum(
                            list(map(int, years_dict[yds].values())))/sum(
                                    list(map(int, years_dict[att].values())))
                elif 'yds/g' in entry:
                    if sum(list(map(int, years_dict[g].values()))) == 0:
                        temp_dict[entry] = 0
                    else:
                        temp_dict[entry] = sum(
                            list(map(int, years_dict[yds].values())))/sum(
                                    list(map(int, years_dict[g].values())))
                # lng = maximum of all lng values present in data
                elif 'lng' in entry:
                    temp_dict[entry] = max(
                            list(map(int, years_dict[entry].values())))
                elif 'att/g' in entry:
                    if sum(list(map(int, years_dict[g].values()))) == 0:
                        temp_dict[entry] = 0
                    else:
                        temp_dict[entry] = sum(
                            list(map(int, years_dict[att].values())))/sum(
                                    list(map(int, years_dict[g].values())))
                # 1st% = first / att
                elif '1st%' in entry:
                    if sum(list(map(int, years_dict[att].values()))) == 0:
                        temp_dict[entry] = 0
                    else:
                        temp_dict[entry] = sum(
                            list(map(int, years_dict[first].values())))/sum(
                                    list(map(int, years_dict[att].values())))
#                elif 'pct' in entry:
#                    pass
#                elif 'td%' in entry:
#                    pass
#                elif 'int%' in entry:
#                    pass
#                elif 'rate' in entry:
#                    pass
                # if the variable is `year` or `team` take the values from the
                #   "newest" entry (i.e. first in order)
                elif entry == 'year' or entry == 'team':
                    temp_dict[entry] =  list(years_dict[entry].values())[0]
                # sum all other variables together to create the new value
                else:                    
                    temp_dict[entry] = sum(
                            list(map(int, years_dict[entry].values())))
            final_list.append(temp_dict)
            
        else:
            # add the data associated with that year to the final list
            final_list.append(annualDF[annualDF['year'] == index].to_dict(
                    orient='records')[0])
            
    return final_list

#==============================================================================
# Working Code
#==============================================================================
          
# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/PlayerStats')

# Iterate over every position folder
for position in position_list:
    try:
        os.chdir(r'/home/ejreidelbach/projects/NFL/Data/PlayerStats/' 
                 + position)  
    except:
        continue

    # Read in all player data from the available JSON files
    files = [f for f in os.listdir('.') if f.endswith(('.json'))]
    files = sorted(files)
    
    stat_list = []
    for file in files:
        with open(file, 'r') as f:
            jsonFile = json.load(f)   
            for player in jsonFile:
                stat_list.append(player)
                
    # Unpack nested career data and situational data for each player
    stat_list_flattened = []
    for row in stat_list:
        # create a deep copy of the row
        player = copy.deepcopy(row)
        
        # pop off the stats_annual and stats_situational elements then iterate 
        #    over them and add their contents back to the basic player info
        try:
            stats_annual = player.pop('stats_annual')
        except:
            print('No Annaul stats found for Player #: ' + 
                  str(stat_list.index(row)) + ' - ' + 
                  player['name_first'] + ' ' + player['name_last'])
        stats_situational = player.pop('stats_situational')
        
        # check to see if any years have multiple stat entries
        # if they do, compress `stats_annual` such that there is only one row
        # row per year and any years with 2 or more teams are reduced to 1
        if len([d['year'] for d in stats_annual]) != len(
                set([d['year'] for d in stats_annual])):
            #print('Multiple years detected for: ' + str(stat_list.index(row)))
            stats_annual = combine_multiyear_stats(stats_annual)
    
        # sort both lists of dictionaries so they're in year order
        stats_annual = sorted(stats_annual, key=lambda k: k['year'])
        stats_situational = sorted(stats_situational, key=lambda k: k['year'])

        # Test to see if there were any issues with compression resulting in 
        #   different numbers of years for annual stats and situational stats
        if len(stats_annual) != len(stats_situational):
            print ('Different year totals for: ' + str(stat_list.index(row)))

        # It's possible that there may not be annual stats or situational stats
        #   in a given year.  To account for this, we have to carefully merge
        #   the two types of stats on a year-by-year basis, inserting empty
        #   values when stats are missing
        years_to_merge = sorted(list(set([d['year'] for d in stats_annual] +
                                  [d['year'] for d in stats_situational])))
        
        # Iterate over every year in the two lists and add the stat list if it
        #   exists for the given year otherwise add None
        stats_combined = []
        for year in years_to_merge:
            stats_combined.append([next((item for item in stats_annual if item[
                    'year'] == year), []), next(
                    (item for item in stats_situational if item[
                    'year'] == year), [])])
    
        # Unpack nested career and situational data by year
        for annual, situation in stats_combined:
            yearPlayer = {}
            yearPlayer.update(player)
            yearPlayer.update(annual)
            yearPlayer.update(situation)
            
            # Calculate player age (12/31 of the given year - player's bday)
            d1 = datetime.strptime(yearPlayer['birthday'], "%m/%d/%Y")
            d2 = '12/31/' + yearPlayer['year']
            d2 = datetime.strptime(d2, "%m/%d/%Y")
            days_between = math.floor(abs((d2-d1).days)/365)
            yearPlayer['age'] = days_between
            
            stat_list_flattened.append(yearPlayer)

    # Correct draft info for each player 
    stat_list_flattened = update_draft_info(stat_list_flattened)

    # Output the flattened list to a CSV
    filename = r'/home/ejreidelbach/projects/NFL/Data/PlayerStats/' + position + '.json'
    with open(filename, 'wt') as out:
        json.dump(stat_list_flattened, out, sort_keys=True, 
                  indent=4, separators=(',', ': '))
    
    # Push the flattened list into a Pandas Dataframe and output it to a CSV
    df = pd.DataFrame(stat_list_flattened)
    filename = r'/home/ejreidelbach/projects/NFL/Data/PlayerStats/' + position + '.csv'
    df.to_csv(filename, index = False)