#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 10:11:51 2018

@author: ejreidelbach

:DESCRIPTION:
    This will serve as the main script for directing the scraping, flattening,
    and analyzing (similarity score processing) of all desired NFL postions.

:REQUIRES:
    This script relies on the other following scripts:
        - analysis_wide_receivers_by_age.py
        - analysis_wide_receivers_by_season.py
        - flatten_NFL_player_stats.py
        - scrape_NFL_player_stats.py   
:TODO:s
"""
 
#==============================================================================
# Package Import
#==============================================================================
import pandas as pd
from pathlib import Path
import os  

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
def ensemble_scores_mean():
    '''
    Description:
        Function that calculates scores for all relevant readability metrics
        utilizing the TEXTATISTIC Python package.  
    
        Details on the package can be found here:
            - https://pypi.org/project/textatistic/
        
    Input:
        document (string): string containing the document to be scored
        
    Output:
        document_dict (dictionary): dictionary containing the resulting scores
            for the document along with counts for total number of words, 
            syllables, and sentences\
    '''
    # find out what folders exist for the various positions
    path_stats = Path('Data','PlayerStats')
    list_positions = os.listdir(path_stats)
    
    # iterate over these existing position folders
    for position in list_positions:
        # Identify all the mean score files in the `PlayerStats` folder
        list_file_median = [f for f in os.listdir(Path(path_stats, position))
                                if 'scores_mean.csv' in str(f)]
        
        # Read in those files
        list_df = []
        for f in list_file_median:
            list_df.append(pd.read_csv(Path(path_stats, position, f), 
                                       index_col = 0))
            
        # Average the contents of every cell across all files
        df_concat = pd.concat(list_df)
        by_row_index = df_concat.groupby(df_concat.index)
        df_means = by_row_index.mean()
        
        # Output the `average` df to a new csv file
        df_means.to_csv(Path(path_stats, position, 
                           f.replace('.csv', '_ensemble.csv')))        

def ensemble_scores_median():
    # find out what folders exist for the various positions
    path_stats = Path('Data','PlayerStats')
    list_positions = os.listdir(path_stats)
    
    # iterate over these existing position folders
    for position in list_positions:
        # Identify all the mean score files in the `PlayerStats` folder
        list_file_median = [f for f in os.listdir(Path(path_stats, position))
                                if 'scores_median.csv' in str(f)]
        
        # Read in those files
        list_df = []
        for f in list_file_median:
            list_df.append(pd.read_csv(Path(path_stats, position, f), 
                                       index_col = 0))
            
        # Average the contents of every cell across all files
        df_concat = pd.concat(list_df)
        by_row_index = df_concat.groupby(df_concat.index)
        df_means = by_row_index.mean()
        
        # Output the `average` df to a new csv file
        df_means.to_csv(Path(path_stats, position, 
                           f.replace('.csv', '_ensemble.csv')))     

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/')


# Create similarity scores files which are ensembles (i.e. averages) of 
#   similarity scores from all files within each category (i.e. median/mean)
#   for all available position groups
ensemble_scores_mean()
ensemble_scores_median()