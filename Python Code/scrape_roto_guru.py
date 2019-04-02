#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 09:15:10 2019

@author: ejreidelbach

:DESCRIPTION:

:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import io
import os  
import pandas as pd
import pathlib
import requests
import tqdm
from bs4 import BeautifulSoup

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

URL_BASE = 'http://rotoguru1.com/cgi-bin/fyday.pl?game=dk&scsv=1&week=WEEK&year=YEAR'
WEEKS = list(map(str, range(1,18)))
YEARS = list(map(str, range(2014,2019)))

# Scrape Draft Kings Data fora ll years
all_games = pd.DataFrame()
for yr in tqdm.tqdm(YEARS):
    for wk in tqdm.tqdm(WEEKS):
        result = requests.get(URL_BASE.replace('WEEK',wk).replace('YEAR',yr))
        soup = BeautifulSoup(result.content)
        all_games = pd.concat([all_games, pd.read_csv(io.StringIO(soup.find('pre').text), sep = ';')])

# Split Name into separate 'NameLast' and 'NameFirst' variables
all_games['NameLast'] = all_games['Name'].apply(lambda x: x.split(',')[0].strip() if ',' in x else '')
all_games['NameFirst'] = all_games['Name'].apply(lambda x: x.split(',')[1].strip() if ',' in x else '')
        
# Rename variable 'h/a'
all_games = all_games.rename(columns = {'h/a':'Home/Away', 'GID':'GameID'})

# Reorder columns
all_games = all_games[['Week',
              'Year',
              'GameID',
              'Name',
              'NameFirst',
              'NameLast',
              'Pos',
              'Team',
              'Home/Away',
              'Oppt',
              'DK points',
              'DK salary'
              ]]

# Export to CSV
all_games.to_csv('DraftKings_2014_to_2018.csv', index = False)