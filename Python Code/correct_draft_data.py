#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 10:43:47 2018

@author: ejreidelbach

:DESCRIPTION:
    - This script will correct any inaccuracies in draft-related information
        that is contained in player statistical data scraped from NFL.com.
    - The draft data obtained for this purpose is from: http://www.drafthistory.com/

:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import json
import os  
import pandas as pd

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================


#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/')

# Import the WR Data
playerDF = pd.read_csv('PlayerStats/WIDE_RECEIVER.csv')

# Import Draft Data
with open('Draft/historic_draft_data.json', 'r') as f:
    draft_list = json.load(f)   
    
# Create a dataframe from the imported json
draftDF = pd.DataFrame(draft_list)

