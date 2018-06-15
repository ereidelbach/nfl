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
    path_stats = Path('Data','PlayerStats')
    list_positions = [os.listdir(path_stats)]
    for file in list_positions:
        file = file.split('_')

    # Identify all the mean score files in the `PlayerStats` folder
    list_file_median = [str(f) for f in os.listdir(Path('Data','PlayerStats'))
                            if 'scores_median.csv' in str(f)]
    
    # Read in those files
    list_df = []
    for f in file_list_median:
        list_df.append(pd.read_csv(f))        
        
    # Average the contents of every cell across all files
    df_avg = pd.DataFrame()
    
    # Output the `average` df to a new csv file
    df_avg.to_csv(')
        

def ensemble_scores_median():
    # Identify all the median score files in the `PlayerStats` folder
    file_list_mean = [str(f) for f in os.scandir(Path(
        'Data','PlayerStats')) if 'scores_mean.csv' in str(f)]
    for f in file_list_mean:
        pass

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