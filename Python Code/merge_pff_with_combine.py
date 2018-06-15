#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 14 15:01:05 2018

@author: ejreidelbach

:DESCRIPTION:
    - Merge positional data scraped from PFF with combine data from the NFL
        website
    
:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import os  
import pandas as pd

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data')

# Load the combine data
df_combine = pd.read_json('Combine/combine_2018.json')

# Load the positional data for Wide Receivers
import json
with open('DraftV2/pff_draft_guide_2018_statistics_WR.json') as f:
    data = json.load(f)
df_pff = pd.DataFrame.from_dict(data)

# rename column `DROP RATE` to `Drop Rate %`:
df_pff.rename(columns={'DROP RATE':'Drop Rate %'}, inplace=True)

# rename column `TEAM` to `college`
df_pff.rename(columns={'TEAM':'college'}, inplace=True)

# convert dtype of columns to numeric (where appropriate)
df_pff = df_pff.apply(pd.to_numeric, errors='ignore')

# force numeric conversion of a few remaining columns via coersion
# strip % values from columns that contain them (detect by finding % in 
#   column name)
col = list(df_pff.columns)
for c in col:
    if '%' in c:
        df_pff[c] = df_pff[c].map(lambda x: str(x).replace('%',''))
        df_pff[c] = pd.to_numeric(df_pff[c], errors='coerce')

df_pff['statsThreeYearTotal.YDS'] = pd.to_numeric(df_pff[
        'statsThreeYearTotal.YDS'], errors='coerce')
df_pff['pffGrade'] = pd.to_numeric(df_pff['pffGrade'], errors='coerce')
df_pff['pffPosRank'] = pd.to_numeric(df_pff['pffPosRank'], errors='coerce')

# convert all df_pff column names to lower case
df_pff.rename(columns = lambda x: x.lower(), inplace=True)
df_pff.rename(columns={'namefirst':'nameFirst',
                       'namelast':'nameLast',
                       'schoolyear':'schoolYear'}, inplace=True)
    
df_wr = pd.merge(df_pff, df_combine, how='left', on=['nameFirst','nameLast','college'])
