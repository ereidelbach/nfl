#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 13:00:45 2019

@author: ejreidelbach

:DESCRIPTION:

:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import numpy as np
import os  
import pandas as pd
import pathlib
import requests
import tqdm

from bs4 import BeautifulSoup, Comment
from requests.packages.urllib3.util.retry import Retry
from string import digits

#==============================================================================
# Reference Variable Declaration
#==============================================================================
list_stats_qb = ['Passing','Rushing & Receiving', 'Defense & Fumbles']
list_stats_rb = ['Rushing & Receiving', 'Defense & Fumbles']
list_stats_wr = ['Receiving & Rushing', 'Defense & Fumbles']
list_stats_def = ['Defense & Fumbles']

dict_column_names = {
        'passing':['Year', 'Age', 'Tm', 'Pos', 'No.', 'G', 'GS', 'QBrec', 
                  'Pass_Cmp', 'Pass_Att', 'Pass_Cmp%', 'Pass_Yds', 'Pass_TD', 
                  'Pass_TD%', 'Pass_Int', 'Pass_Int%', 'Pass_Lng', 'Pass_Y/A', 
                  'Pass_AY/A', 'Pass_Y/C', 'Pass_Y/G', 'Pass_Rate', 'Pass_QBR', 
                  'Pass_Sk', 'Pass_Yds.1', 'Pass_NY/A', 'Pass_ANY/A', 
                  'Pass_Sk%', 'Pass_4QC', 'Pass_GWD'
                  ],
        'rushing':['Year', 'Age', 'Tm', 'Pos', 'No.', 'G', 'GS', 'Rush_Rush', 
                  'Rush_Yds', 'Rush_TD', 'Rush_Lng', 'Rush_Y/A', 'Rush_Y/G', 
                  'Rush_A/G', 'Rec_Tgt','Rec_Rec', 'Rec_Yds', 'Rec_Y/R', 
                  'Rec_TD', 'Rec_Lng', 'Rec_R/G', 'Rec_Y/G', 'Rec_Ctch%', 
                  'Total_Touch', 'Total_Y/Tch', 'Total_YScm', 'Total_RRTD', 
                  'Fmb'
                  ],
        'receiving':['Year', 'Age', 'Tm', 'Pos', 'No.', 'G', 'GS', 'Rec_Tgt', 
                     'Rec_Rec', 'Rec_Yds', 'Rec_Y/R', 'Rec_TD', 'Rec_Lng', 
                     'Rec_R/G', 'Rec_Y/G', 'Rec_Ctch%', 'Rush_Rush', 'Rush_Yds',
                     'Rush_TD', 'Rush_Lng', 'Rush_Y/A', 'Rush_Y/G', 'Rush_A/G',
                     'Total_Touch', 'Total_Y/Tch', 'Total_YScm', 'Total_RRTD',
                     'Fmb'
                     ],
        'defense':['Year', 'Age', 'Tm', 'Pos', 'No.', 'G', 'GS', 'Int',
                   'Int_Yds', 'Int_TD', 'Int_Lng', 'PD', 'FF', 'Fmb', 'FR', 
                   'Fmb_Yds', 'Fmb_TD', 'Sk', 'Tkl_Comb', 'Tkl_Solo', 
                   'Tkl_Ast', 'TFL', 'QBHits', 'Sfty'
                  ]
        }

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

def extractColumnNames(list_columns):
    '''
    Extract column names given a multi-tiered column list (i.e. tuples)
    '''
    list_columns_new = []
    for pair in list_columns:
        if any(x in pair[0] for x in ['Unnamed', 'Games']):
            list_columns_new.append(pair[1])
        elif 'Rushing' in pair[0]:
            list_columns_new.append('Rush_' + pair[1])
        elif 'Receiving' in pair[0]:
            list_columns_new.append('Rec_' + pair[1])
        elif 'Total Yds' in pair[0]:
            list_columns_new.append('Tot_' + pair[1])         
        elif 'Def Interceptions' in pair[0]:
            list_columns_new.append('INT_' + pair[1])
        elif 'Fumbles' in pair[0]:
            list_columns_new.append('Fum_' + pair[1])
        elif 'Tackles' in pair[0]:
            list_columns_new.append('Tkl_' + pair[1])       
    return list_columns_new

def retrievePlayerList(category, year):
    '''
    Purpose: Obtain a list of basic player information from sports-reference 
        for a given year and statistical category    
        
    Inputs
    ------
        category : string
            category for which players are to be scraped (passing, rushing, 
            receiving and defense)
        year : string
            year for which players are to be scraped (i.e. 2018)
    
    Outputs
    -------
        list_players : list of dictionaries
            contains a list of player-specific dictionaries; each dictionary
            contains the players name, pro-reference ID and pro-reference URL   
    '''
    # set the url to be scraped
    url = 'https://www.pro-football-reference.com/years/%s/%s.htm' % (year, category)    

    # scrape the page
    soup = soupifyURL(url)
    
    # retrieve the table of player stats
    table = soup.find('table', {'id':category})
    
    # create a list for storing all player dictionaries
    list_players = []
    
    # retrieve player name and ID for each player in the table
    for row in table.findAll('tr')[1:]:
        # ignore rows that do not contain player data
        if '<tr class="thead">' in str(row):
            pass
        else:
            # try-except catches any rows without data
            try:
                dict_player = {}
                dict_player['name'] = row.find('td').find('a').text
                dict_player['href'] = row.find('td').find('a')['href']
                dict_player['ID'] = row.find('td').find(
                        'a')['href'].split('/')[3].split('.htm')[0]
                list_players.append(dict_player)
            except:
                pass
            
    return list_players

def renameSchool(df, name_var):
    '''
    Purpose: Rename a school/university to a standard name as specified in 
        the file `school_names_pictures.csv`

    Inputs
    ------
        df : Pandas Dataframe
            DataFrame containing a school-name variable
        name_var : string
            Name of the variable which is to be renamed/standardized
    
    Outputs
    -------
        df : Pandas Dataframe
            DataFrame containing the standardized team name 
    '''  
    # read in school name information
    df_school_names = pd.read_csv(path_dir.joinpath(
            'Data/school_names_pictures.csv'))    
     
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
            
    def swapSchoolName(name_old):
        if name_old == 'nan':
            return ''
        try:
            return dict_school_names[name_old]
        except:
            print('Did not find: %s' % (name_old))
            return name_old
            
#    df[name_var] = df[name_var].apply(
#            lambda x: dict_school_names[x] if str(x) != 'nan' else '')
    df[name_var] = df[name_var].apply(lambda x: swapSchoolName(x))
    
    return df  

def renameNFL(df, name_var):
    '''
    Purpose: Rename an NFL team to a standardized name as specified in 
        the file `nfl_names_pictures.csv`

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
    df_school_names = pd.read_csv(path_dir.joinpath(
            'Data/nfl_names_pictures.csv'))    
     
    # convert the dataframe to a dictionary such that the keys are the
    #   optional spelling of each school and the value is the standardized
    #   name of the school
    dict_school_names = {}
    
    for index, row in df_school_names.iterrows():
        # isolate the alternative name columns
        names = row[[x for x in row.index if 'name' in x.lower()]]
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
            dict_school_names[name_alternate] = name_standardized
            
    def swapSchoolName(name_old):
        if name_old == 'nan':
            return ''
        try:
            return dict_school_names[name_old]
        except:
            print('Did not find: %s' % (name_old))
            return name_old
            
    df[name_var] = df[name_var].apply(lambda x: swapSchoolName(x))
    
    return df  

def standardizeLogoNCAA(df):
    '''
    Purpose: Fill in the value of the NCAA logo field for all players in a DF

    Inputs
    ------
        df : Pandas Dataframe
            Contains all the player information and metadata
            
    Outputs
    -------
        urls_ncaa : list of strings
            Standardized version of all school logo URLs
    '''    
    # ingest the school names and URLs from a flat file    
    df_pictures = pd.read_csv('Data/school_names_pictures.csv')

    # create a dictionary where the team name is the key and the url is the value
    df_pictures.set_index('Team', drop=True, inplace=True)
    dict_pictures = df_pictures.to_dict('index')
    for key, value in dict_pictures.items():
        dict_pictures[key] = value['urlSchool']
    
    # create the variable 'pictureSchoolURL' to store each team's logo URL
    df['pictureSchoolURL'] = df['School'].apply(lambda x: dict_pictures[x])
    
    return df

def standardizeLogoNFL(df):
    '''
    Purpose: Fill in the value of the NFL logo field for all players in a DF

    Inputs
    ------
        df : Pandas Dataframe
            Contains all the player information and metadata
            
    Outputs
    -------
        urls_ncaa : list of strings
            Standardized version of all school logo URLs
    '''    
    # ingest the school names and URLs from a flat file    
    df_pictures = pd.read_csv('Data/nfl_names_pictures.csv')

    # create a dictionary where the team name is the key and the url is the value
    df_pictures.set_index('Team', drop=True, inplace=True)
    dict_pictures = df_pictures.to_dict('index')
    for key, value in dict_pictures.items():
        dict_pictures[key] = value['URL']

    def standardizeName(team):
        try:
            return dict_pictures[team]
        except:
            print('Logo not found for %s' % (team))
            return ''
    
    # create the variable 'pictureSchoolNFL' to store each team's logo URL
    df['pictureSchoolNFL'] = df['Tm'].apply(lambda x: standardizeName(x))
    
    return df

def scrapePlayerHistory(player):
    '''
    Purpose: Scrape historical player data (on a seasonal level) from 
        sports-reference for a given player
        
    Inputs
    ------
        player : doctionary
            keys are 'name', 'href', and 'ID' which correspond to a player's
            full name, sports-reference URL and a sports-reference ID
    
    Outputs
    -------
        df_player : Pandas DataFrame
            dataframe containing detailed statistical data for a player's career
    '''
    # set the player's url
    url_player = 'https://www.pro-football-reference.com/%s' % player['href']
    
    # scrape the player's page
    soup = soupifyURL(url_player)
    
    #--- obtain basic player information -------------------------------------#
    info = soup.find('div', {'id':'meta'})
    # player picture
    try:
        pictureURL = info.find('img')['src']
    except:
        pictureURL = ''
    # first name and last name
    try:
        nameFirst = player['name'].split(' ')[0]
    except:
        nameFirst = ''
    try:
        nameLast = ' '.join(player['name'].split(' ')[1:])
    except:
        nameLast = ''
    # player position
    try:
        position = info.find(
            'strong', text='Position').next_sibling.strip().split(': ')[1]
    except:
        position = ''
    if position in ['P', 'K']:
        return
    # player height and weight -- convert height to inches and weights to lbs
    try:
        height = info.find('span', {'itemprop':'height'}).text
        height = int(height.split("-")[0])*12 + int(height.split("-")[1])
    except:
        height = np.nan
    try:
        weight = info.find('span', {'itemprop':'weight'}).text
        weight = int(''.join(c for c in weight if c in digits))
    except:
        weight = np.nan
    # player birthday and birthplace
    try:
        birthday = info.find('span', {'itemprop':'birthDate'})['data-birth']
    except:
        birthday = '0000-00-00'
    try:
        birthplace = ' '.join(info.find('span', {
            'itemprop':'birthPlace'}).text.strip().split('\xa0')[1:])
    except:
        birthplace = ''
    # player's college and URL/ID used on sports-reference.com
    try:
        college = info.find('strong', text='College').next_sibling.next_sibling.text
    except:
        college = ''
    try:
        collegeURL = (info.find('strong', text='College').next_sibling.
                      next_sibling.next_sibling.next_sibling['href'])
        collegeID = collegeURL.split('/')[-1].replace('.html','')
    except:
        collegeURL = ''
        collegeID = ''

    # create a list for storing all player data
    list_player_data = []
    
    #--- obtain player historical statistics ---------------------------------#
    # passing data (EASY)
    try:
        df_temp = pd.read_html(str(soup.find('table', {'id':'passing'})))[0]
        # rename columns (requires special code as AV not always present)
        if 'AV' in df_temp.columns:
            av = df_temp['AV']
            df_temp.drop(columns = ['AV'], axis = 1, inplace = True)
            df_temp.columns = (['Year','Age','Tm','Pos','No.','G','GS','QBrec'] 
                                + ['Pass_' + x for x in df_temp.columns[8:]])
            df_temp['AV'] = av
        else:
            df_temp.columns = dict_column_names['passing']
        # add to list
        list_player_data.append(df_temp)
    except:
        pass  
    
    # rushing data    
    for cat_id in ['rushing_and_receiving', 'receiving_and_rushing', 'defense']:
        try:
            table = soup.find('div', {'id':'div_'+cat_id}).find('table')
            df_temp = pd.read_html(str(table))[0]
            # rename columns (requires special code as AV not always present)
            df_temp.columns = extractColumnNames(df_temp.columns.tolist())
            # add to list
            list_player_data.append(df_temp)
        except:
            pass      
    # search for data that is commented out
    commented_data = soup.find_all(string=lambda text:isinstance(text,Comment))
    for comment in commented_data:
        soup_comment = BeautifulSoup(str(comment), 'lxml')
        # test for rushing, receiving or defense data and add it if found
        for cat_id in ['rushing_and_receiving', 'receiving_and_rushing', 'defense']:
            try:
                #create a dataframe of the data
                df_temp = pd.read_html(str(
                        soup_comment.find('table', {'id':cat_id})))[0]
                # rename columns (requires special code as AV not always present)
                df_temp.columns = extractColumnNames(df_temp.columns.tolist())
                # add to list of player's historical data
                list_player_data.append(df_temp)
            except:
                pass
    
    #---- Conduct Dataframe Cleanup ------------------------------------------#
    # account for years in which a player missed the season due to injury
    list_clean_data = []
    for df in list_player_data:
        for column in df.columns.tolist():
            df[column] = df[column].apply(
                    lambda x: np.nan if 'Missed season' in str(x) else x)
        # drop career stats
        df = df.iloc[:df[df['Year'] == 'Career'].index[0]]
        # remove % from percentage variables
        for column in [x for x in df.columns.tolist() if '%' in x]:
            df[column] = df[column].apply(lambda x: float(str(x).replace('%','')))
        # set data types for all columns
        df = df.astype({'Pos':str})
        columns_numeric = [x for x in df.columns.tolist() if x not in [
                'Tm', 'Pos', 'Year', 'QBrec']]
        df[columns_numeric] = df[columns_numeric].apply(
                pd.to_numeric, errors = 'ignore')
        list_clean_data.append(df)
        
    list_player_data = list_clean_data.copy()       
    
    # make a dataframe out of the list of lists (merge each df in the list)
    df_player = pd.DataFrame()
    if len(list_player_data) > 1:
        for count in range(0, len(list_player_data)-1):
            if count == 0:
                df_player = pd.merge(list_player_data[count], 
                                     list_player_data[count+1],
                                     how = 'outer')
            else:
                df_player = pd.merge(df_player, list_player_data[count+1],
                                     how = 'outer')
    elif len(list_player_data) == 1:
        df_player = list_player_data[0]
    else:
        print("No data found for %s" % (player['name']))
    
    # add basic player information to the dataframe
    df_player['Player'] = player['name']
    df_player['nameFirst'] = nameFirst
    df_player['nameLast'] = nameLast
    df_player['position'] = position
    df_player['birthday'] = birthday
    try:
        df_player['hometownCity'] = birthplace.split(', ')[0]
    except:
        df_player['hometownCity'] = ''
        print(birthplace)
    try:
        df_player['hometownState'] = birthplace.split(', ')[1]
    except:
        df_player['hometownState'] = ''
        print(birthplace)
    df_player['heightInches'] = height
    df_player['Weight'] = weight
    df_player['School'] = college
    df_player['urlSportsRefNFL'] = url_player
    df_player['picturePlayerURL'] = pictureURL
    df_player['urlSportsRefNCAA'] = collegeURL
    df_player['ID_SportsRef_ncaa'] = collegeID
    df_player['ID_SportsRef_nfl'] = player['ID']
    
    # account for pro bowl years
    #   * == Pro Bowl
    #   + == First-Team All-Pro
    df_player['ProBowl'] = df_player['Year'].apply(
            lambda x: 1 if '*' in str(x) else 0) 
    df_player['AllPro'] = df_player['Year'].apply(
            lambda x: 1 if '+' in str(x) else 0)
    df_player['Year'] = df_player['Year'].apply(
            lambda x: ''.join(c for c in str(x) if c in digits))     
    
    return df_player    

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
path_dir = pathlib.Path('/home/ejreidelbach/Projects/NFL')
os.chdir(path_dir)

# Iterate over four different statistical categories
for category in ['passing', 'rushing', 'receiving', 'defense']:

    list_players_category = []
    
    # Iterate over all years from 2005 to 2018
    for year in list(map(str, range(2005,2019))):
        list_players_category.append(retrievePlayerList(category, year))
        
    # flatten scraped list of players into one master list
    list_players_flattened = [player for sublist in list_players_category 
                         for player in sublist]
    
    # deduplicate flattened list (sourced code snippet from: 
    #   https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python)
    list_players_flattened = [i for n, i in enumerate(
            list_players_flattened) if i not in list_players_flattened[n + 1:]]
        
    # create a list for storing all player historical data
    list_player_stats = []
    
    # Use the list of all players to scrape player historical stats
    for dict_player in list_players_flattened:
        list_player_stats.append(scrapePlayerHistory(dict_player))
        
    # convert the list of dataframes into a single dataframe
    df_category = pd.concat(list_player_stats, sort = False)
    
    # standardize all college names
    df_category = renameSchool(df_category, 'School')
    
    # standardize all NFL names
    df_category = renameNFL(df_category, 'Tm')
        
    # create a variable for NCAA logos ('pictureSchoolURL')
    df_category = standardizeLogoNCAA(df_category)
    
    # create a variable for NFL logos ('pictureNflURL')
    df_category = standardizeLogoNFL(df_category)
    
    # for quarterback data, break out the win/loss record when starting games
    if category == 'passing':
        df_category['GS_W'] = df_category['QBrec'].apply(
                lambda x: int(x.split('-')[0]) if not pd.isna(x) else 0)
        df_category['GS_L'] = df_category['QBrec'].apply(
                lambda x: int(x.split('-')[1]) if not pd.isna(x) else 0)
        df_category['GS_T'] = df_category['QBrec'].apply(
                lambda x: int(x.split('-')[2]) if not pd.isna(x) else 0)
        df_category['GS_W%'] = df_category.apply(lambda row:
                round((row['GS_W'] / row['GS'])*100, 1) 
                if row['GS'] != 0 else np.nan, axis =1)
        df_category.drop(columns = ['QBrec'], axis = 1, inplace = True)
        
    # reorder column variables as desired
            
    # Export the dataframe to disk