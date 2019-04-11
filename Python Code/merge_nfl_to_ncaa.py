#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 10:04:09 2019

@author: ejreidelbach

:DESCRIPTION:
    Merges NFL data scraped from pro-reference with college data scraped from
        sports-reference and ESPN (meta_DEF.csv and meta_OFF.csv).

:REQUIRES:
    Refer to the Package Import section of the script
    
:TODO:
    TBD
"""
 
#==============================================================================
# Package Import
#==============================================================================
import json
import os  
import numpy as np
import pandas as pd
import pathlib
import tqdm

from ast import literal_eval
from functools import reduce

#==============================================================================
# Reference Variable Declaration
#==============================================================================
dict_sort_variable = {'LB':'lastTackles',
                      'DB':'lastPBU',
                      'DL':'lastTFL',
                      'Other':'lastTackles',
                      'QB':'last',
                      'RB':'last',
                      'WR':'last',
                      'TE':'last',
                      }
dict_positions = {'LB':['LB', 'OLB', 'ILB', 'MLB'],
                  'DB':['CB', 'S', 'DB'],
                  'DL':['DE', 'DT', 'DL', 'NT'],
                  'QB':['QB'],
                  'RB':['SB','HB','RB','FB'],
                  'WR':['WR'],
                  'TE':['TE'],
        }
list_variables_nfl = ['Year',
                      'Age',
                      'position_nfl',
                      'Player',
                      'Team',
                      'height_nfl',
                      'weight_nfl',
                      'School',
                      'ID_SportsRef_ncaa',
                      'ID_SportsRef_nfl',
                      'picturePlayerURL',
                      ]
list_variables_ncaa = ['unique_id',
                       'Player',
                       'School',
                       'position_0',
                       'position_1',
                       'position_2',
                       'height',
                       'weight',
                       'draftPick',
                       'draftRound',
                       'draftTeam',
                       'draftYear',
                       'picturePlayerURL'
                       ]
list_variables_merged = ['player',
                         'year_last', 
                         'age_last',
                         'id_ncaa',
                         'id_nfl',
                         'school',
                         'pos_ncaa0',
                         'pos_ncaa1',
                         'pos_ncaa2',
                         'team_nfl',
                         'pos_nfl',
                         'height_ncaa',
                         'weight_ncaa',
                         'height_nfl',
                         'weight_nfl',
                         'draft_overall',
                         'draft_round',
                         'draft_team',
                         'draft_year',
                         'url_pic_player'
                         ]
dict_var_rename = {'Year':'year_last',
                   'Team':'team_nfl', 
                   'Age':'age_last', 
                   'height':'height_ncaa', 
                   'weight':'weight_ncaa',
                   'ID_SportsRef_ncaa':'id_ncaa',
                   'ID_SportsRef_nfl':'id_nfl',
                   'position_0':'pos_ncaa0',
                   'position_1':'pos_ncaa1',
                   'position_2':'pos_ncaa2',
                   'position_nfl':'pos_nfl',
                   'draftPick':'draft_overall',
                   'draftRound':'draft_round',
                   'draftTeam':'draft_team',
                   'draftYear':'draft_year',
                   'Player':'player',
                   'School':'school',
                   'picturePlayerURL':'url_pic_player',
                   'heightNFL':'height_nfl',
                   }
#==============================================================================
# Function Definitions
#==============================================================================
def ingest_data_ncaa():
    '''
    '''
    # ingest the college data for offense and defense
    df_off = pd.read_csv('positionData/Metadata/meta_OFF.csv')
    df_def = pd.read_csv('positionData/Metadata/meta_DEF.csv')
    
    # limit the datasets to just the variables we care about
    df_off = df_off[list_variables_ncaa]
    df_def = df_def[list_variables_ncaa]
    
    # merge the two datasets together
    df_merge = pd.merge(df_off, df_def, how = 'outer',
                        on = ['unique_id'])
    
    # clean up duplicate variables
    for variable in ['Player', 'School', 'position_0', 'position_1', 
                     'position_2', 'height', 'weight', 'draftPick',
                     'draftRound', 'draftTeam', 'draftYear', 
                     'picturePlayerURL']:
        # keep the _x version of the variable unless it is missing, then go with _y
        df_merge[variable] = df_merge.apply(lambda row:
            row['%s_x' % variable] if pd.isna(row['%s_y' % variable]) 
            else row['%s_y' % variable], axis = 1)
        # drop _x and _y variables once merged variable is created
        df_merge = df_merge.drop(
                ['%s_x' % variable, '%s_y' % variable], axis = 1)    

    # drop any potential duplicates
    df_merge = df_merge.drop_duplicates()
    
    return df_merge

def ingest_data_nfl():
    '''
    '''
    # ingest the nfl data
    df_passing = pd.read_csv('positionData/scraped_NFL/passing-2005-2018.csv')
    df_receiving = pd.read_csv('positionData/scraped_NFL/receiving-2005-2018.csv')
    df_rushing = pd.read_csv('positionData/scraped_NFL/rushing-2005-2018.csv')
    df_defense = pd.read_csv('positionData/scraped_NFL/defense-2005-2018.csv')
    
    # create a new variable for NFL height (format: Ft - Inches)
    def add_height_variable(df):
        return df['heightInches_nfl'].apply(
            lambda x: '-'.join([
                    str(int(np.floor(x/12))), 
                    str(int(x - np.floor(x/12)*12))]) if not pd.isna(x) else '')
        
    df_passing['height_nfl'] = add_height_variable(df_passing)
    df_receiving['height_nfl'] = add_height_variable(df_receiving)
    df_rushing['height_nfl'] = add_height_variable(df_rushing)
    df_defense['height_nfl'] = add_height_variable(df_defense)
    
    # limit the datasets to just the variables we care about
    df_passing = df_passing[list_variables_nfl]
    df_receiving = df_receiving[list_variables_nfl]
    df_rushing = df_rushing[list_variables_nfl]
    df_defense = df_defense[list_variables_nfl]
    
    # merge the two datasets together
    def merge_nfl_sets(df1, df2):
        df_merge = pd.merge(df1, df2, 
                            how = 'outer',
                            on = ['ID_SportsRef_nfl'])
        # clean up duplicate variables
        for variable in ['Year',
                         'Age',
                         'position_nfl',
                         'Player',
                         'Team',
                         'height_nfl',
                         'weight_nfl',
                         'School',
                         'ID_SportsRef_ncaa',
                         'picturePlayerURL']:
            # keep the _x version of the variable unless it is missing, then go with _y
            df_merge[variable] = df_merge.apply(lambda row:
                row['%s_x' % variable] if pd.isna(row['%s_y' % variable]) 
                else row['%s_y' % variable], axis = 1)
            # drop _x and _y variables once merged variable is created
            df_merge = df_merge.drop(
                    ['%s_x' % variable, '%s_y' % variable], axis = 1)    

        # drop any potential duplicates
        df_merge = df_merge.drop_duplicates()
        
        return df_merge
    
    df_merge = merge_nfl_sets(df_passing, df_receiving)
    df_mergeV2 = merge_nfl_sets(df_merge, df_rushing)
    df_mergeV3 = merge_nfl_sets(df_mergeV2, df_defense)
    
    # only keep the last year for all players
    df_nfl = df_mergeV3.drop_duplicates(subset = ['ID_SportsRef_nfl'], 
                                        keep = 'last')    
    # reorder dataframe
    df_nfl = df_nfl[list_variables_nfl]    
    
    return df_nfl
    
#    # ingest the nfl data
#    df_nfl = pd.DataFrame()
#    for cat in ['passing', 'receiving', 'rushing', 'defense']:
#        df_temp = pd.read_csv('positionData/scraped_NFL/%s-2005-2018.csv' % cat)
#        if len(df_nfl) == 0:
#            df_nfl = df_temp.copy()
#        else:
#            df_nfl = pd.concat([df_nfl, df_temp], sort = False, 
#                                       ignore_index = True)
#
#    # only keep desired variables
#    df_nfl = df_nfl[list_variables_nfl]
#            
#    # only keep the last year for all players
#    df_nfl.drop_duplicates(inplace = True, subset = ['ID_SportsRef_nfl'], 
#                                   keep = 'last')       
#    
#    # clean up duplicate variables
#    for variable in ['Player', 'School', 'position_0', 'position_1', 
#                     'position_2', 'height', 'weight', 'draftPick',
#                     'draftRound', 'draftTeam', 'draftYear', 
#                     'picturePlayerURL']:
#        for index, row in test.iterrows():
#            if (row['%s_x' % variable] != '') and (row['%s_y' % variable] != ''):
#                if row['%s_x' % variable] != row['%s_y' % variable]:
#                    print('Mismatch for %i -- %s -- variable %s' % 
#                          (index, row['unique_id'], variable))
#    
#    
#    # ingest the college data
#    df_ncaa = pd.DataFrame()
#    for cat in ['OFF', 'DEF']:
#        df_temp = pd.read_csv('positionData/Metadata/meta_%s.csv' % cat)
#        if len(df_ncaa) == 0:
#            df_ncaa = df_temp.copy()
#        else:
#            df_ncaa = pd.concat([df_ncaa, df_temp], sort = False, 
#                                ignore_index = True)
#    # only keep desired variables
#    df_ncaa = df_ncaa[list_variables_ncaa]
#  
#    # picturePlayerURL seems to be causing a lot of duplications
#    df_ncaa = df_ncaa.fillna('')
#    dict_pictures = {}
#    for index, row in df_ncaa.iterrows():
#        if row['picturePlayerURL'] != '':
#            dict_pictures[row['unique_id']] = row['picturePlayerURL']
#    df_ncaa['picturePlayerURL'] = df_ncaa.apply(lambda row:
#        dict_pictures[row['unique_id']] if row['unique_id'] 
#        in dict_pictures.keys() else '', axis = 1)
#    
#    # remove duplicates that may exist across position groups
#    df_ncaa.drop_duplicates(inplace = True)    
#    
#    
#    df_ncaa['duplicated'] = df_ncaa.duplicated(subset = ['unique_id'], keep = False)
#    df_ncaa.to_csv('positionData/Metadata/dupes.csv', index = False)    

def merge_nfl_ncaa_metadata():
    '''
    Purpose: Given scraped NFL metadata (from pro-football-reference.com) and
        scraped NCAA metadata (from sports-reference.com), merge the two 
        together to obtain a final, cohesive metadata record that spans both
        leagues for all players.
        
    Inputs
    ------
    
    Outputs
    -------
        df_merged : Pandas DataFrame
            Contains merged metadata for all players for both NCAA and NFL data        
    '''
    # ingest the data
    df_ncaa = ingest_data_ncaa()
    df_nfl = ingest_data_nfl()
            
    # merge the nfl and college data
    df_merged = pd.merge(df_nfl, df_ncaa, how = 'outer',
                                 left_on = 'ID_SportsRef_ncaa', 
                                 right_on = 'unique_id')
      
    # fill in variables to account for overlap across the two files
    for variable in ['Player', 'School', 'picturePlayerURL']:
        # keep the _x version of the variable unless it is missing, then go with _y
        df_merged[variable] = df_merged.apply(lambda row:
            row['%s_x' % variable] if pd.isna(row['%s_y' % variable]) 
            else row['%s_y' % variable], axis = 1) 
        
    # drop _x and _y variables once merged variable is created
    for variable in ['Player', 'School', 'picturePlayerURL']:
        df_merged = df_merged.drop(
                ['%s_x' % variable, '%s_y' % variable], axis = 1)
        
    # merge the contents of 'unique_id' and 'ID_SportsRef_ncaa'
    df_merged['ID_SportsRef_ncaa'] = df_merged.apply(lambda row:
        row['ID_SportsRef_ncaa'] if pd.isna(row['unique_id']) 
        else row['unique_id'], axis = 1)     

    # drop the variable 'unique_id' as it is no longer used
    df_merged = df_merged.drop('unique_id', axis = 1)
        
#    # create a new variable for NFL height (format: Ft - Inches)
#    df_merged['heightNFL'] = df_merged['heightInches_nfl'].apply(
#            lambda x: '-'.join([
#                    str(int(np.floor(x/12))), 
#                    str(int(x - np.floor(x/12)*12))]) if not pd.isna(x) else '')
#    
#    # correct issues where countries are stored in the city field
#    list_states = df_merged.apply(lambda row:
#        row['hometownCity'] if pd.isna(row['hometownState']) 
#        else row['hometownState'], axis = 1)
#    df_merged['hometownCity'] = df_merged.apply(lambda row:
#        '' if pd.isna(row['hometownState']) else row['hometownCity'], axis = 1)
#    df_merged['hometownState'] = list_states.copy()
#        
#    # fill in missing values with empty strings for hometownState and hometownCity
#    df_merged[['hometownCity', 'hometownState']] = df_merged[[
#            'hometownCity', 'hometownState']].fillna('')
#        
#    # fill in missing hometown values by recreating the variable
#    df_merged['hometown'] = df_merged.apply(lambda row:
#        ', '.join([row['hometownCity'], row['hometownState']]) 
#        if row['hometownCity'] != '' else row['hometownState'], axis = 1)
        
    # rename variables as desired
    df_merged = df_merged.rename(dict_var_rename, axis = 1)
    
    # put dataframe columns in desired order
    df_merged = df_merged[list_variables_merged]
    
    # sort the dataframe by last name (i.e. 'name_last')
    df_merged = df_merged.sort_values(by = 'id_ncaa')
    
#    # test for duplicates
#    df_merged['ncaa_dup'] = df_merged.duplicated(subset = ['id_ncaa'], keep = False)
#    df_merged['ncaa_dup'].value_counts()[1]
#    df_merged['nfl_dup'] = df_merged.duplicated(subset = ['id_nfl'], keep = False)
#    df_merged['nfl_dup'].value_counts()[1]
    
    # export the dataframe to a csv file
    df_merged.to_csv('positionData/Metadata/merged.csv', index = False)
    
    return df_merged

def merge_combine_data():
    '''
    Purpose: Merges NFL combine data with pre-existing metadata already
        scraped from sports-reference.com for NFL and college players
        
    Inputs
    ------
        category : string
            Category of statistics to be merging -- offense or defense
    
    Outputs
    -------
        df_merge : Pandas DataFrame
            The data resulting from the merge of the original, player metadata
            with any relevant combine information obtained by matching on 
            the 'id_sr_ncaa' variable
    '''
    # ingest the data to be merged
    df_combine = pd.read_csv('positionData/Combine/combine_2000_to_2020.csv')
    df_position = pd.read_csv('positionData/Metadata/merged.csv')
    
    # subset the combine data to only what we need for merging
    df_combine = df_combine[['Ht', 'Wt', '40yd', 'Vertical', 
                             'Bench', 'Broad Jump', '3Cone', 'Shuttle',
                             'DraftTeam', 'DraftRound', 'DraftPick',
                             'DraftYear', 'id_sr_ncaa', 'id_sr_nfl']]
    
    # rename combine variables
    df_combine = df_combine.rename({'DraftPick':'draft_overall',
                                    'DraftRound':'draft_round',
                                    'DraftTeam':'draft_team',
                                    'DraftYear':'draft_year',
                                    'Ht':'combine_height',
                                    'Wt':'combine_weight',
                                    '40yd':'combine_40yd',
                                    'Vertical':'combine_vertical',
                                    'Bench':'combine_bench',
                                    'Broad Jump':'combine_broad_jump',
                                    '3Cone':'combine_3cone',
                                    'Shuttle':'combine_shuttle',
                                    'id_sr_ncaa':'id_ncaa',
                                    'id_sr_nfl':'id_nfl'}, axis = 1)


    #----------------------- Merge on Both NCAA and NFL ----------------------#
    df_merge_both = pd.merge(df_position, df_combine[pd.notnull(
            df_combine.id_ncaa) & pd.notnull(df_combine.id_nfl)], 
            how = 'left', on = ['id_ncaa', 'id_nfl'])
    
    # clean up duplicate variables
    for variable in ['draft_overall', 'draft_round', 'draft_team', 
                     'draft_year']:
        # keep the _x version of the variable unless it is missing, then go with _y
        df_merge_both[variable] = df_merge_both.apply(lambda row:
            row['%s_x' % variable] if pd.isna(row['%s_y' % variable]) 
            else row['%s_y' % variable], axis = 1)
        # drop _x and _y variables once merged variable is created
        df_merge_both = df_merge_both.drop(
                ['%s_x' % variable, '%s_y' % variable], axis = 1)
        
    # drop players that don't have a value for 'id_ncaa' and 'id_nfl'
    df_merge_both = df_merge_both[~pd.isna(df_merge_both['id_ncaa']) & 
                                  ~pd.isna(df_merge_both['id_nfl'])]
    
    #----------------------- Merge on only NCAA ------------------------------#
    df_merge_ncaa = pd.merge(df_position, df_combine[pd.notnull(
            df_combine.id_ncaa) & pd.isna(df_combine.id_nfl)], 
            how = 'left', on = 'id_ncaa')
    
    # clean up duplicate variables
    for variable in ['draft_overall', 'draft_round', 'draft_team', 
                     'draft_year', 'id_nfl']:
        # keep the _x version of the variable unless it is missing, then go with _y
        df_merge_ncaa[variable] = df_merge_ncaa.apply(lambda row:
            row['%s_x' % variable] if pd.isna(row['%s_y' % variable]) 
            else row['%s_y' % variable], axis = 1)
        # drop _x and _y variables once merged variable is created
        df_merge_ncaa = df_merge_ncaa.drop(
                ['%s_x' % variable, '%s_y' % variable], axis = 1)
        
    # drop players that don't have a value for 'id_ncaa'
    df_merge_ncaa = df_merge_ncaa[pd.notnull(df_merge_ncaa['id_ncaa']) & 
                                  pd.isnull(df_merge_ncaa['id_nfl'])]
    
    #----------------------- Merge on only NFL --------------------------------#
    df_merge_nfl = pd.merge(df_position, df_combine[pd.notnull(
            df_combine.id_nfl) & pd.isna(df_combine.id_ncaa)], 
            how = 'left', on = 'id_nfl')
    
    # clean up duplicate variables
    for variable in ['draft_overall', 'draft_round', 'draft_team', 
                     'draft_year', 'id_ncaa']:
        # keep the _x version of the variable unless it is missing, then go with _y
        df_merge_nfl[variable] = df_merge_nfl.apply(lambda row:
            row['%s_x' % variable] if pd.isna(row['%s_y' % variable]) 
            else row['%s_y' % variable], axis = 1)
        # drop _x and _y variables once merged variable is created
        df_merge_nfl = df_merge_nfl.drop(
                ['%s_x' % variable, '%s_y' % variable], axis = 1)
        
    # drop players that don't have a value for 'id_nfl'
    df_merge_nfl = df_merge_nfl[pd.notnull(df_merge_nfl['id_nfl']) & 
                                pd.isnull(df_merge_nfl['id_ncaa'])]
        
    #----------------------- Stitch together ---------------------------------#
    df_merge = pd.concat([df_merge_both, df_merge_ncaa, df_merge_nfl], sort = False)
    df_merge = df_merge.drop_duplicates()
    
#    #----------------------- Merge NCAA data ---------------------------------#
#    df_merge = pd.merge(df_position, df_combine[pd.notnull(
#            df_combine.id_ncaa)], how = 'left', on = 'id_ncaa')
#    
#    # clean up duplicate variables
#    for variable in ['draft_overall', 'draft_round', 'draft_team', 
#                     'draft_year', 'id_nfl']:
#        # keep the _x version of the variable unless it is missing, then go with _y
#        df_merge[variable] = df_merge.apply(lambda row:
#            row['%s_x' % variable] if pd.isna(row['%s_y' % variable]) 
#            else row['%s_y' % variable], axis = 1)
#        # drop _x and _y variables once merged variable is created
#        df_merge = df_merge.drop(
#                ['%s_x' % variable, '%s_y' % variable], axis = 1)
#
#    #----------------------- Merge NFL data ----------------------------------#
#    df_merge = pd.merge(df_position, df_combine[pd.notnull(
#            df_combine.id_nfl)], how = 'left', on = 'id_nfl')
#    
#    # clean up duplicate variables
#    for variable in ['draft_overall', 'draft_round', 'draft_team', 
#                     'draft_year', 'id_ncaa']:
#        # keep the _x version of the variable unless it is missing, then go with _y
#        df_merge[variable] = df_merge.apply(lambda row:
#            row['%s_x' % variable] if pd.isna(row['%s_y' % variable]) 
#            else row['%s_y' % variable], axis = 1)
#        # drop _x and _y variables once merged variable is created
#        df_merge = df_merge.drop(
#                ['%s_x' % variable, '%s_y' % variable], axis = 1)
        
    # standardize NFL names for 'draft_team'
    df_merge = rename_nfl(df_merge, 'draft_team')
    
    # reorder variables
    df_merge = df_merge[['player', 'year_last', 'age_last', 'id_ncaa', 'id_nfl',
                         'school', 'pos_ncaa0', 'pos_ncaa1', 'pos_ncaa2', 
                         'team_nfl', 'pos_nfl', 'height_ncaa', 'weight_ncaa',
                         'height_nfl', 'weight_nfl', 'draft_overall', 
                         'draft_round', 'draft_team', 'draft_year', 
                         'combine_height', 'combine_weight', 'combine_40yd',
                         'combine_vertical', 'combine_bench', 
                         'combine_broad_jump', 'combine_3cone', 
                         'combine_shuttle', 'url_pic_player',
                         ]]

    # test for duplicates
    df_merged = df_merge.copy()
    df_merged['ncaa_dup'] = df_merged.duplicated(subset = ['id_ncaa'], keep = False)
    df_merged[df_merged['ncaa_dup'] == True]['id_ncaa'].value_counts()
    df_merged['nfl_dup'] = df_merged.duplicated(subset = ['id_nfl'], keep = False)
    df_merged[df_merged['nfl_dup'] == True]['id_nfl'].value_counts()
        
    # write it to a csv
    df_merge.to_csv('positionData/Metadata/merged_with_combine.csv', index = False)
    
    return df_merge

def remove_duplicates(df_all):
    '''
    Purpose: Despite multiple de-duplication attemps, some duplicates still 
        remain. This is because there is no connection between the id_nfl 
        and the id_ncaa, but the players are still the same.
        
    Inputs
    ------
        df_all : Pandas DataFrame
            Metadata for all players (containing the duplicate entries)
    
    Outputs
    -------
        df_fixed : Pandas Dataframe
            Metadata for all players (with no more duplicate entries)
    '''
    df_all = df_all.reset_index(drop = True)
    
    # by matching on 'player' and 'school' we can isolate duplicate entries
    df_broken = df_all[df_all.duplicated(subset = ['player', 'school'], 
                                         keep = False)]
        
    # subset the ok rows so we don't have to worry abou them
    df_ok = df_all[~df_all.index.isin(df_broken.index)]
    
    # group by player name and school
    grouped = df_broken.groupby(['player', 'school'])
    
    # iterate through each group
    list_data_fixed = []
    for name, group in grouped:
        # retrieve the data from the group
        data = grouped.get_group(name)
        list_player = []
        # iterate over each column and grab the non-missing data for the player
        for col in data.columns:
            # if the group is only one player, stop there and grab it
            if len(data) == 1:
                list_player.append(data[col].iloc[0])
            # if the first row of data is not missing grab it
            elif pd.notna(data[col].iloc[0]):
                list_player.append(data[col].iloc[0])
            # otherwise check to see if the second row of data is not missing 
            elif pd.notna(data[col].iloc[1]):
                list_player.append(data[col].iloc[1])
            # if both are missing, insert an NA value
            else:
                list_player.append(np.nan)
        list_data_fixed.append(list_player)
    # convert the reduced list of lists into a dataframe
    df_fixed = pd.DataFrame(list_data_fixed)
    
    # set the columns of df_fixed to equal df_ok
    df_fixed.columns = df_ok.columns
            
    # merge all the data back together again, minus the duplicates
    df_final = pd.concat([df_ok, df_fixed], sort = False)
    
    return df_final

def output_to_json(df_output):
    '''
    Purpose: Output a metadata file to JSON format for use in the draft-gem
        ecosystem (will serve as a player lookup table for all desired metadata).
    
    Inputs
    ------
        df_output_off : Pandas DataFrame
            Metadata for all offensive players
        df_output_def : Pandas DataFrame
            Metadata for all defensive players
            
    Outputs
    -------
        dict_meta : JSON file
            JSON formatted Metadata that is written to a file in the 
            'positionData/Metadata' folder    
    '''
    # reset table index
    df_output = df_output.reset_index(drop = True)
      
    # standardize NFL positions to be one of 7 categories [QB, RB, WR, TE, 
    #   DL, DB, LB]
    df_output['pos_nfl_std'] = df_output['pos_nfl'].apply(lambda x: standardize_positions_nfl(str(x)))
    
    # standardize NFL names such that they are formatted like: Minnesota Vikings
    df_output = rename_nfl(df_output, 'team_nfl')

    # fill in missing values with blanks rather than float NaNs
    df_output = df_output.fillna('')
    
    # output to csv
    df_output.to_csv('positionData/Metadata/metadata_final.csv', index = False)
    
    # Convert the dataframe to a dictionary
    dict_meta = df_output.to_dict('records')    
    
    # Write dictionary to a .json file
    with open('positionData/Metadata/metadata_final.json', 'wt') as out:
            json.dump(dict_meta, out, sort_keys=True) 

def rename_nfl(df, name_var):
    '''
    Purpose: Rename an NFL team to a standardized name as specified in 
        the file `names_pictures_nfl.csv`

    Inputs
    ------
        df : Pandas Dataframe
            DataFrame containing an NFL-name variable
        name_var : string
            Name of the variable which is to be renamed/standardized
    
    Outputs
    -------
        df : Pandas Dataframe
            DataFrame containing the standardized team name
    '''  
    # read in school name information
    df_team_names = pd.read_csv(path_dir.joinpath(
            'positionData/names_pictures_nfl.csv'))    
     
    # convert the dataframe to a dictionary such that the keys are the
    #   optional spelling of each team and the value is the standardized
    #   name of the team
    dict_team_names = {}
    
    for index, row in df_team_names.iterrows():
        # isolate the alternative name columns
        names = row[[x for x in row.index if 'name' in x.lower()]]
        names.pop('URL_NAME')
        # convert the row to a list that doesn't include NaN values
        list_names_nicknames = [
                x for x in names.values.tolist() if str(x) != 'nan']
        # extract the standardized team name
        name_standardized = row['Team']
        # add the standardized name
        list_names_nicknames.append(name_standardized)
        # for every alternative spelling of the team, set the value to be
        #   the standardized name
        for name_alternate in list_names_nicknames:
            dict_team_names[name_alternate] = row['FullName']
            
    def swapteamName(name_old):
        if ((name_old == 'nan') or (pd.isna(name_old)) or 
             (name_old == 'none') or (name_old == '')):
            return ''
        try:
            return dict_team_names[name_old]
        except:
            print('Did not find: %s' % (name_old))
            return name_old
            
    df[name_var] = df[name_var].apply(lambda x: swapteamName(x))
    
    return df   
    
def standardize_positions_nfl(position):
    '''
    Purpose: Standardize the positions of NFL players such that they fall
        in one of the following groups: [QB, RB, WR, TE, DB, DL, LB]
        
    Inputs
    ------
        position : string    
            The original version of the position a player plays, scraped from
            Pro Football Reference
            
    Outputs
    -------
        position_new : string
            The standardized version of a player's position
    '''
    for pos in dict_standardize_positions:
        if pos in position:
            return dict_standardize_positions[pos]
#    try:
#        if any(pos in position for pos in ['QB']):
#            return 'QB'
#        elif any(pos in position for pos in ['RB', 'FB', 'HB', 'SB']):
#            return 'RB'
#        elif any(pos in position for pos in ['WR', 'SE',]):
#            return 'WR'
#        elif any(pos in position for pos in ['TE']):
#            return 'TE'
#        elif any(pos in position for pos in ['DE', 'DT', 'DL', 'NT']):
#            return 'DL'     
#        elif any(pos in position for pos in ['LB', 'ILB', 'OLB']):
#            return 'LB'   
#        elif any(pos in position for pos in position in ['S', 'CB', 'DB', 'FS', 'SS']):
#            return 'DB'
#        else:
#            print('Position "%s" does not match any in our lookup table' % position)
#            return ''
#    except:
#        print('error encountered')
#        print(position)
        
dict_standardize_positions = {
        'QB':'QB',
        'RB':'RB',
        'FB':'RB',
        'HB':'RB',
        'SB':'RB',
        'WR':'WR',
        'SE':'WR',
        'TE':'TE',
        'DE':'DL',
        'DL':'DL',
        'DT':'DL',
        'NT':'DL',
        'LB':'LB',
        'ILB':'LB',
        'OLB':'LB',
        'CB':'DB',
        'DB':'DB',
        'FS':'DB',
        'S':'DB',
        'SS':'DB',        
        'K':'',
        'KR':'',
        'LS':'',
        'C':'',
        'G':'',
        'OG':'',
        'OL':'',
        'OT':'',
        'P':'',
        'PK':'',
        'PR':'',
        'T':'',
        }
#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
path_dir = pathlib.Path('/home/ejreidelbach/Projects/draft-gem/src/static/')
os.chdir(path_dir)

#------------------------------------------------------------------------------
# Step 1. Combine NFL data with it's collegiate counterpart's metadata
#------------------------------------------------------------------------------ 
df = merge_nfl_ncaa_metadata()

#------------------------------------------------------------------------------
# Step 2. Combine merged data with combine data
#------------------------------------------------------------------------------
dfV2 = merge_combine_data()

#------------------------------------------------------------------------------
# Step 3. Write metadata to JSON file for upload to draft-gem current version
#------------------------------------------------------------------------------
dfV3 = remove_duplicates(dfV2)

#------------------------------------------------------------------------------
# Step 3. Write metadata to JSON file for upload to draft-gem current version
#------------------------------------------------------------------------------
output_to_json(dfV3)
 