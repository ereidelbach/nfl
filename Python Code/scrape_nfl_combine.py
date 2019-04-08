#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 14:38:34 2019

@author: ejreidelbach

:DESCRIPTION: Scrapes combine data from 2000 to 2018 from ProFootball Reference
    'https://www.pro-football-reference.com/draft/2019-combine.htm'

:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import datetime
import os  
import pandas as pd
import pathlib
import requests
import tqdm
import time

from bs4 import BeautifulSoup
from requests.packages.urllib3.util.retry import Retry
from string import digits

#==============================================================================
# Reference Variable Declaration
#==============================================================================

#==============================================================================
# Function Definitions
#==============================================================================
def soupifyURL(url):
    '''
    Purpose: Turns a specified URL into BeautifulSoup formatted HTML 

    Inputs
    ------
        url : string
            Link to the designated website to be scraped
    
    Outputs
    -------
        soup : html
            BeautifulSoup formatted HTML data stored as a complex tree of 
            Python objects
    '''
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    r = session.get(url)
    #r = requests.get(url)
    soup = BeautifulSoup(r.content,'html.parser')   
    return soup

def renameSchool(df, name_var):
    '''
    Purpose: Rename a school/university to a standard name as specified in 
        the file `school_abbreviations.csv`

    Inputs
    ------
        df : Pandas Dataframe
            DataFrame containing a school-name variable for which the names
            need to be standardized
        name_var : string
            Name of the variable which is to be renamed/standardized
    
    Outputs
    -------
        list(row)[0] : string
            Standardized version of the school's name based on the first value
            in the row in the file `school_abbreviations.csv`
    '''  
    # read in school name information
    df_school_names = pd.read_csv('/home/ejreidelbach/Projects/draft-gem/' +
                                  'src/static/positionData/' +
                                  'pics.csv')
     
    # convert the dataframe to a dictionary such that the keys are the
    #   optional spelling of each school and the value is the standardized
    #   name of the school
    dict_school_names = {}
    
    for index, row in df_school_names.iterrows():
        # isolate the alternative name columns
        names = row[[x for x in row.index if 'Name' in x]]
        # convert the row to a list that doesn't include NaN values
        list_names = [x for x in names.values.tolist() if str(x) != 'nan']
        # add the nickname to the team names as an alternative name
        nickname = row['Nickname']
        list_names_nicknames = list_names.copy()
        for name in list_names:
            list_names_nicknames.append(name + ' ' + nickname)
        # extract the standardized team name
        name_standardized = row['Team']
        # add the standardized name
        list_names_nicknames.append(name_standardized)
        # add the nickname to the standardized name
        list_names_nicknames.append(name_standardized + ' ' + nickname)
        # for every alternative spelling of the team, set the value to be
        #   the standardized name
        for name_alternate in list_names_nicknames:
            dict_school_names[name_alternate] = name_standardized
            
    df[name_var] = df[name_var].apply(
            lambda x: dict_school_names[x] if str(x) != 'nan' else '')
        
    return df    

def scrapeCombineAllYears():
    '''
    Purpose: Scrape combine information for all players for all years
        that is provided by pro-football-reference.com (sports-reference)
        [https://www.pro-football-reference.com/draft/2019-combine.htm]
        
    Inputs
    ------
        NONE
    
    Outputs
    -------
        df_master : Pandas DataFrame
            contains combine information for all players from all scraped years
    '''  
    # create a list for storing data from all years
    list_dfs = []
    
    # process all available years
    year_end = datetime.datetime.now().year + 1
    year_start = 2000
    
    # Scrape data for all available years
    for year in tqdm.tqdm(list(range(year_start, year_end))):
        
        # scrape page for combine year
        url = ('https://www.pro-football-reference.com/draft/' 
               + str(year) + '-combine.htm')
        soup = soupifyURL(url)
        
        # Test for a year with no data (happens in new year w/o combine)
        if 'Page Not Found' in str(soup):
            continue
        
        # Retrieve the HTML of the combine table
        table = soup.find('table', {'id':'combine'})
        
        # Convert the table to a dataframe
        df_year = pd.read_html(str(table))[0]
        df_year['Year'] = year
        
        # Drop Rows that contain header information (i.e. 'Player' == 'Player')
        df_year = df_year[df_year['Player'] != 'Player']
        
        # Retrieve player's nfl/ncaa ID and profile URL
        list_player_urls_nfl = []
        list_player_ids_nfl = []
        list_player_urls_ncaa = []
        list_player_ids_ncaa = []
        for row in table.find_all('tr'):
            # the first column of each row contains the nfl data
            col = row.find('th')
            if col.text != 'Player':
                if col.find('a') is not None:
                    list_player_urls_nfl.append(col.a['href'])
                    list_player_ids_nfl.append(col['data-append-csv'])
                else:
                    list_player_urls_nfl.append('')
                    list_player_ids_nfl.append('')
            # after that, the 3rd column over has the ncaa data
            col = row.find_all('td')
            if col != []:
                if col[2].find('a') is not None:
                    list_player_urls_ncaa.append(col[2].a['href'])
                    list_player_ids_ncaa.append(
                            col[2].a['href'].split('/')[-1].split('.html')[0])
                else:
                    list_player_urls_ncaa.append('')
                    list_player_ids_ncaa.append('')           
                    
        # Create the variables: 'id_sr_ncaa', 'url_sr_ncaa', 'id_sr_nfl', 'url_sr_nfl'
        df_year['id_sr_ncaa'] = list_player_ids_ncaa
        df_year['url_sr_ncaa'] = list_player_urls_ncaa
        df_year['id_sr_nfl'] = list_player_ids_nfl
        df_year['url_sr_nfl'] = list_player_urls_nfl
        
        # Add the data for the year to the list
        list_dfs.append(df_year)
        
        # Wait a second to slow down the rate of scraping
        time.sleep(1)
        
    # convert the data from all years into one file
    df_master = pd.DataFrame()
    for df in list_dfs:
        if len(df_master) == 0:
            df_master = df.copy()
        else:
            df_master = df_master.append(df)
  
    # Standardize Variables and Formatting of dataframe
    df_final = fixCombineInfo(df_master)
    
    # Write the file to csv
    df_final.to_csv('positionData/Combine/combine_%s_to_%s.csv' % 
                    (year_start, year_end), index = False)
        
    return df_final

def scrapeCombineSpecificYear(year):
    '''
    Purpose: Scrape combine information for all players for the specified year.
        Data is scraped from pro-football-reference.com (sports-reference)
        [https://www.pro-football-reference.com/draft/2019-combine.htm]
        
    Inputs
    ------
        year : int
            desired year of combine info to scrape 
    
    Outputs
    -------
        df_master : Pandas DataFrame
            contains combine information for all players from all scraped years
    '''  
    # scrape data for requested year
    url = ('https://www.pro-football-reference.com/draft/' 
           + str(year) + '-combine.htm')
    soup = soupifyURL(url)

    # Retrieve the HTML of the combine table    
    table = soup.find('table', {'id':'combine'})

    # Convert the table to a dataframe    
    df_year = pd.read_html(str(table))[0]
    df_year['Year'] = year  
    
    # Drop Rows that contain header information (i.e. 'Player' == 'Player')
    df_year = df_year[df_year['Player'] != 'Player']
    
    # Retrieve player's nfl/ncaa ID and profile URL
    list_player_urls_nfl = []
    list_player_ids_nfl = []
    list_player_urls_ncaa = []
    list_player_ids_ncaa = []
    for row in table.find_all('tr'):
        # the first column of each row contains the nfl data
        col = row.find('th')
        if col.text != 'Player':
            if col.find('a') is not None:
                list_player_urls_nfl.append(col.a['href'])
                list_player_ids_nfl.append(col['data-append-csv'])
            else:
                list_player_urls_nfl.append('')
                list_player_ids_nfl.append('')
        # after that, the 3rd column over has the ncaa data
        col = row.find_all('td')
        if col != []:
            if col[2].find('a') is not None:
                list_player_urls_ncaa.append(col[2].a['href'])
                list_player_ids_ncaa.append(
                        col[2].a['href'].split('/')[-1].split('.html')[0])
            else:
                list_player_urls_ncaa.append('')
                list_player_ids_ncaa.append('')           
                
    # Create the variables: 'id_sr_ncaa', 'url_sr_ncaa', 'id_sr_nfl', 'url_sr_nfl'
    df_year['id_sr_ncaa'] = list_player_ids_ncaa
    df_year['url_sr_ncaa'] = list_player_urls_ncaa
    df_year['id_sr_nfl'] = list_player_ids_nfl
    df_year['url_sr_nfl'] = list_player_urls_nfl

    # Standardize Variables and Formatting of dataframe
    df_final = fixCombineInfo(df_year)
    
    return df_final
        
def fixCombineInfo(df_input):
    '''
    Purpose: Standardize combine information (including fixing variables
        and creating new ones)
        
    Inputs
    ------
        df_input : Pandas DataFrame
            contains combine information
    
    Outputs
    -------
        df : Pandas DataFrame
            contains combine information with standardized/corrected information
    '''
    df = df_input.copy()

    # remove the stats variable `College` which contained a link that didn't soupify
    df.drop(columns = ('College'), inplace = True)

    # set data types of numeric variables to a float
    df[['Wt', '40yd', 'Vertical', 'Bench', 'Broad Jump', '3Cone', 'Shuttle', 
        'Year']] = df[['Wt', '40yd', 'Vertical', 'Bench', 'Broad Jump', 
               '3Cone', 'Shuttle', 'Year']].apply(lambda x: x.astype(float))
    
    # split the `Drafted (tm/rnd/yr)` variable into 3 variables (1 for each category)
    df['DraftTeam'] = df['Drafted (tm/rnd/yr)'].apply(
            lambda x: x.split('/')[0].strip() if not pd.isna(x) else '')
    df['DraftRound'] = df['Drafted (tm/rnd/yr)'].apply(
            lambda x: x.split('/')[1].strip()[0] if not pd.isna(x) else '')
    df['DraftPick'] = df['Drafted (tm/rnd/yr)'].apply(
            lambda x: x.split('/')[2].strip() if not pd.isna(x) else '')
    df['DraftPick'] = df['DraftPick'].apply(lambda pick:
            ''.join(x for x in pick if x in digits))
    df['DraftYear'] = df['Drafted (tm/rnd/yr)'].apply(
            lambda x: x.split('/')[-1].strip() if not pd.isna(x) else '')
        
    # remove the old `Drafted (tm/rnd/yr)` variable
    df.drop(columns = ('Drafted (tm/rnd/yr)'), inplace = True)
    
    # add a `HeightInches` variable
    df['HtInches'] = df['Ht'].apply(lambda height:
            (int(height.split("-")[0])*12 + int(height.split("-")[1])))
        
    # add the nameFirst and nameLast variables
    df['nameFirst'] = df['Player'].apply(lambda x: x.split(' ')[0])
    df['nameLast'] = df['Player'].apply(lambda x: ' '.join(x.split(' ')[1:]))
        
    # reorder the columns
    df = df[['Year', 'Player', 'nameFirst', 'nameLast', 'Pos', 'School', 'Ht', 
             'HtInches', 'Wt', '40yd', 'Vertical', 'Bench', 'Broad Jump',
             '3Cone', 'Shuttle', 'DraftTeam', 'DraftRound',
             'DraftPick', 'DraftYear', 'id_sr_ncaa', 'id_sr_nfl',
             'url_sr_ncaa', 'url_sr_nfl']]
        
    return df

#=============================================================================
# Working Code
#==============================================================================

# Set the project working directory
path_dir = pathlib.Path('/home/ejreidelbach/Projects/draft-gem/src/static')
os.chdir(path_dir)

# Scrape Data for all years
df = scrapeCombineAllYears()

# Scrape Data for specific years
#df = scrapeCombineSpecificYear(2019)    