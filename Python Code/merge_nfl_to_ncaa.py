#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 10:04:09 2019

@author: ejreidelbach

:DESCRIPTION:
    Merges NFL data scraped from pro-reference with college data scraped from
        sports-reference.

:REQUIRES:
    Refer to the Package Import section of the script
    
:TODO:
    TBD
"""
 
#==============================================================================
# Package Import
#==============================================================================
import os  
import pandas as pd
import pathlib
import tqdm

#==============================================================================
# Reference Variable Declaration
#==============================================================================

#==============================================================================
# Function Definitions
#==============================================================================
def function_name(var1, var2):
    '''
    Purpose: Stuff goes here

    Inputs   
    ------
        var1 : type
            description
        var2 : type
            description
            
    Outputs
    -------
        var1 : type
            description
        var2 : type
            description
    '''
#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
path_dir = pathlib.Path('/home/ejreidelbach/Projects/')
os.chdir(path_dir)

   
#------------------------------------------------------------------------------
# fill in missing values with blanks rather than float NaNs
df_final = df_final.fillna('')
    
# Convert the dataframe to a dictionary
dict_final = df_final.to_dict('records')    

# Write updated data (with paths to pictures vice URLs) to a .json file 
#   ('pos_POSITION_final_pics.json')
with open('Data/SportsReference/qb_lookup.json', 'wt') as out:
    json.dump(dict_final, out, sort_keys=True) 