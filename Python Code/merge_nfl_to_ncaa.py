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
                      'nameFirst',
                      'nameLast',
                      'Team',
                      'birthday',
                      'hometownCity',
                      'hometownState',
                      'heightInches_nfl',
                      'weight_nfl',
                      'School',
                      'ID_SportsRef_ncaa',
                      'ID_SportsRef_nfl',
                      'urlSportsRefNCAA',
                      'urlSportsRefNFL',
                      'picturePlayerURL',
                      'pictureNflURL',
                      'pictureSchoolURL'
                      ]
list_variables_merged = ['player',
                         'school',
                         'team_nfl',
                         'pos_nfl',
                         'pos_sr_0',
                         'pos_sr_1',
                         'pos_sr_2',
                         'pos_espn',
                         'name_first',
                         'name_last',
                         'name_espn',
                         'age_last',
                         'year_last',
                         'height_nfl',
                         'height_inches_nfl',
                         'weight_nfl',
                         'height_ncaa',
                         'heightInches_ncaa',
                         'weight_ncaa',
                         'home',
                         'home_city',
                         'home_state',
                         'birthday',
                         'draft_overall',
                         'draft_round',
                         'draft_team',
                         'draft_year',
                         'id_sr_ncaa',
                         'id_sr_nfl',
                         'url_sr_ncaa',
                         'url_sr_nfl',
                         'url_espn_ncaa',
                         'url_pic_player',
                         'url_pic_team_ncaa',
                         'url_pic_team_nfl'
                         ]
dict_var_rename = {'Year':'year_last',
                   'Team':'team_nfl', 
                   'Age':'age_last', 
                   'height':'height_ncaa', 
                   'heightInches':'heightInches_ncaa',
                   'weight':'weight_ncaa',
                   'ID_SportsRef_ncaa':'id_sr_ncaa',
                   'ID_SportsRef_nfl':'id_sr_nfl',
                   'urlSportsRefNCAA':'url_sr_ncaa',
                   'urlSportsRefNFL':'url_sr_nfl',
                   'pictureNflURL':'url_pic_team_nfl',
                   'nameESPN':'name_espn',
                   'position_0':'pos_sr_0',
                   'position_1':'pos_sr_1',
                   'position_2':'pos_sr_2',
                   'position_nfl':'pos_nfl',
                   'positionESPN':'pos_espn',
                   'draftPick':'draft_overall',
                   'draftRound':'draft_round',
                   'draftTeam':'draft_team',
                   'draftYear':'draft_year',
                   'hometown':'home',
                   'urlESPN':'url_espn_ncaa',
                   'Player':'player',
                   'School':'school',
                   'nameFirst':'name_first',
                   'nameLast':'name_last',
                   'hometownCity':'home_city',
                   'hometownState':'home_state',
                   'picturePlayerURL':'url_pic_player',
                   'pictureSchoolURL':'url_pic_team_ncaa',
                   'heightNFL':'height_nfl',
                   'heightInches_nfl':'height_inches_nfl'
                   }
#==============================================================================
# Function Definitions
#==============================================================================
def merge_nfl_ncaa_metadata(category):
    '''
    Purpose: Given scraped NFL metadata (from pro-football-reference.com) and
        scraped NCAA metadata (from sports-reference.com), merge the two 
        together to obtain a final, cohesive metadata record that spans both
        leagues for all players.
        
    Inputs
    ------
        category : string
            Type of data to merge (Two options: 'offense' or 'defense')
    
    Outputs
    -------
        df_merged : Pandas DataFrame
            Contains merged metadata for all players for both NCAA and NFL data        
    '''
    # error catcher -- only 'offense' and 'defense' are valid categories
    if category not in ['offense', 'defense']:
        print('Wrong category selected.  Please enter "offense" or "defense."')
        return
    
    # ingest the nfl data
    if category == 'offense':
        df_nfl = pd.DataFrame()
        for sub_cat in ['passing', 'receiving', 'rushing']:
            df_temp = pd.read_csv('positionData/scraped_NFL/%s-2005-2018.csv' % sub_cat)
            if len(df_nfl) == 0:
                df_nfl = df_temp.copy()
            else:
                df_nfl = pd.concat([df_nfl, df_temp], sort = False, 
                                           ignore_index = True)
    elif category == 'defense':
        df_nfl = pd.read_csv('positionData/scraped_NFL/%s-2005-2018.csv' % category)
    
    # remove duplicates that may exist across position groups
    df_nfl.drop_duplicates(inplace = True)
    
    # only keep the last year for all players
    df_nfl.drop_duplicates(inplace = True, subset = ['ID_SportsRef_nfl'], 
                                   keep = 'last')
    
    # only keep desired variables
    df_nfl = df_nfl[list_variables_nfl]
    
    # ingest the college data
    if category == 'offense':
        df_ncaa = pd.read_csv('positionData/Metadata/meta_OFF.csv')
    elif category == 'defense':
        df_ncaa = pd.read_csv('positionData/Metadata/meta_DEF.csv')
            
    # merge the nfl and college data
    df_merged = pd.merge(df_nfl, df_ncaa, how = 'outer',
                                 left_on = 'ID_SportsRef_ncaa', 
                                 right_on = 'unique_id')
      
    # fill in variables to account for overlap across the two files
    for variable in ['Player', 'School', 'nameFirst', 'nameLast', 'hometownCity',
                     'hometownState', 'picturePlayerURL', 'pictureSchoolURL',
                     'birthday']:
        # keep the _x version of the variable unless it is missing, then go with _y
        df_merged[variable] = df_merged.apply(lambda row:
            row['%s_x' % variable] if pd.isna(row['%s_y' % variable]) 
            else row['%s_y' % variable], axis = 1) 
        # drop _x and _y variables once merged variable is created
        df_merged = df_merged.drop(
                ['%s_x' % variable, '%s_y' % variable], axis = 1)
        
    # create a new variable for NFL height (format: Ft - Inches)
    df_merged['heightNFL'] = df_merged['heightInches_nfl'].apply(
            lambda x: '-'.join([
                    str(int(np.floor(x/12))), 
                    str(int(x - np.floor(x/12)*12))]) if not pd.isna(x) else '')
    
    # correct issues where countries are stored in the city field
    list_states = df_merged.apply(lambda row:
        row['hometownCity'] if pd.isna(row['hometownState']) 
        else row['hometownState'], axis = 1)
    df_merged['hometownCity'] = df_merged.apply(lambda row:
        '' if pd.isna(row['hometownState']) else row['hometownCity'], axis = 1)
    df_merged['hometownState'] = list_states.copy()
        
    # fill in missing values with empty strings for hometownState and hometownCity
    df_merged[['hometownCity', 'hometownState']] = df_merged[[
            'hometownCity', 'hometownState']].fillna('')
        
    # fill in missing hometown values by recreating the variable
    df_merged['hometown'] = df_merged.apply(lambda row:
        ', '.join([row['hometownCity'], row['hometownState']]) 
        if row['hometownCity'] != '' else row['hometownState'], axis = 1)
        
    # rename variables as desired
    df_merged = df_merged.rename(dict_var_rename, axis = 1)
        
    # drop the variable 'unique_id' as it is no longer used
    df_merged = df_merged.drop('unique_id', axis = 1)
    
    # put dataframe columns in desired order
    df_merged = df_merged[list_variables_merged]
    
    # sort the dataframe by last name (i.e. 'name_last')
    df_merged = df_merged.sort_values(by = 'name_last')
    
    # export the dataframe to a csv file
    df_merged.to_csv('positionData/MetaData/merged_%s.csv' % category, 
                     index = False)
    
    return df_merged

def subsetDataByPosition(df_pos, position):
    '''
    Purpose: Given a DataFrame of players for a specific category of football
        data (i.e. Passing, Rushing, Receiving or Defense), subset that data
        such that individual files are created for specific positions.
        
        For example, given Passing data, subset the data such that only players
        who played quarterback are in the data and save it as 'pos_QB.csv'

    Inputs
    ------
        df_pos : Pandas Dataframe
            DataFrame containing player information for a specific stat group
                (i.e. Passing, Rushing, Receiving or Defensive)
        position : string
            Position group for which data exists and must be merged
            (options are 'DEF', 'QB', RB', and 'WR')
    
    Outputs
    -------
        The subset dataframe is written to a .json and .csv file in /public
    '''    

    # reduce the dataset to contain only players of specific positions'
    list_cols_pos = [x for x in df_pos.columns.tolist() if 'position' in x]
    df_subset = pd.DataFrame()
    # iterate over every position column and add players if they played that pos
    for col in list_cols_pos:
        players = df_pos[df_pos[col].isin(dict_positions[position])]
        if len(df_subset) == 0:
            df_subset = players.copy()
        else:
            df_subset = pd.concat([df_subset, players] , sort = False)
            
    # remove any duplicate rows created in this process
    df_subset = df_subset.drop_duplicates()
    
    # sort the reduced dataset by the desired variable for the position group
    df_subset = df_subset.sort_values(by = [dict_sort_variable[position]], 
                                      ascending = False)
    
    # reset index
    df_subset = df_subset.reset_index(drop = True)
    
    # create the `Index` variable
    df_subset['Index'] = df_subset.index
        
    #------ Make sure columns with ELO data are stored as lists  of ints -----#
    # obtain a list of all elo variables
    list_elo = [x for x in list(df_subset.columns) if 'elo' in x.lower()]
    # iterate through each elo variable and eval it so that it's a list
    for elo in list_elo:
        df_subset[elo] = df_subset[elo].apply(lambda x: literal_eval(x))
        
    #-------- Make sure opponent ids are stored as list of ints --------------#
    list_temp = []
    for row in df_subset['opp']:
        try:
            list_temp.append([int(x) for x in row.split(',')])
        except:
            list_temp.append('')
            print(row)
    df_subset['opp'] = list_temp
    
    #-------- Make sure the date column is stored as a list of string --------#
    list_temp = []
    for row in df_subset['date']:
        list_temp.append([str(x) for x in row.split(',')])
    df_subset['date'] = list_temp
    #df_subset['date'] = df_subset['date'].apply(lambda x: literal_eval(x))
    
    # fill in missing values with blanks rather than float NaNs
    df_subset = df_subset.fillna('')
    
    # make a new position variable and drop others
    df_subset['position'] = position
    df_subset = df_subset.drop(list_cols_pos[:-1], axis = 1)
    list_cols_new = df_subset.columns.tolist()
    list_cols_new.insert(6, list_cols_new.pop(len(list_cols_new)-1))
    df_subset = df_subset[list_cols_new]
    
    return df_subset

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
path_dir = pathlib.Path('/home/ejreidelbach/Projects/draft-gem/src/static/')
os.chdir(path_dir)

#------------------------------------------------------------------------------
# Step 1. Combine NFL data with it's collegiate counterpart
#------------------------------------------------------------------------------
# OFFENSE 
df_off = merge_nfl_ncaa_metadata('offense')
 
# DEFENSE      
df_def = merge_nfl_ncaa_metadata('defense')