#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 10:30:08 2019

@author: ejreidelbach

:DESCRIPTION:
    - This script will scrape player historical data from ESPN.com
    
:REQUIRES:
    
:TODO:
    - Account for additional column header in kicker information regarding
        yardage kicks were attempted from
        ** example page: http://www.nfl.com/player/gregzuerlein/2534797/careerstats
"""
 
#==============================================================================
# Package Import
#==============================================================================
import cutie
import json
import os
import requests
import tqdm

from bs4 import BeautifulSoup
from pathlib import Path
from requests.packages.urllib3.util.retry import Retry

#==============================================================================
# Reference Variable Declaration
#============================================================================== 

#==============================================================================
# Function Definitions
#==============================================================================
def askUserForInput():
    '''
    Purpose: On the command line, ask the user to input which position they 
        would like to scrape player-specific page URLs for as well as what year
        data is requested for.  If the user does  not want to scrape URLs for 
        all positions, they will be asked what posiiton they are specifically 
        interested in.
        
    Inputs
    ------
        NONE
        
    Outputs
    -------
        scrape_position : string
            Position that the user requests data for 
            (allowed values are 'QB', 'RB', 'WR', 'TE', or 'ALL')
            [default = 'all']
    '''
    #-------------------------- POSITION --------------------------------------
    # Set the default for scraping to all positions
    scrape_position = 'all'
    
    # Prompt the user to select the years they would like to scrape URLs for
    list_all = ['Would you like to scrape URLS for all positions?', 
                'No',
                'Yes'
                ]
    all_positions = list_all[
            cutie.select(
                    list_all, 
                    caption_indices=[0],
                    selected_index=1)]
                
    # If the user wants all position URLs
    if all_positions == 'Yes':
        print('Proceeding to scrape URLs for all available positions.') 
        scrape_position = ['QB', 
                           'WR', 
                           'RB', 
                           'TE']
    # If the user wants URLs for a specific position
    else:
        positions = ['Select the position for which you would like to ' + 
                     'scrape URLs:',
                     'QB', 
                     'RB', 
                     'WR', 
                     'TE']
        scrape_position = [positions[cutie.select(positions, 
                                                  caption_indices=[0], 
                                                  selected_index=1)]]
        print(f'User selected: {scrape_position}')

    #-------------------------- YEAR RANGE ------------------------------------
    # Set the default for scraping to all positions
    scrape_year = 'all'
    
    # Prompt the user to select the years they would like to scrape URLs for
    list_all = ['Would you like to scrape URLS for all available years ' + 
                '(2002-current)?', 
                'No',
                'Yes'
                ]
    all_years = list_all[
            cutie.select(
                    list_all, 
                    caption_indices=[0],
                    selected_index=1)]
        
    # What year does the user want data for (go back to 2002)
    if all_years == 'Yes':
        print('Proceeding to scrape URLs for all available years.')
        scrape_year = ['2018', '2017', '2016', '2015', '2014', '2013', '2012', 
                       '2011', '2010', '2009', '2008', '2007', '2006', '2005', 
                       '2004', '2003', '2002']
    # If the user wants URLs for a specific year
    else:
        years = ['Select the year for which you would like to scrape URLs:',
                 '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011',
                 '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003',
                 '2002']
        scrape_year = [years[cutie.select(years, caption_indices=[0], 
                                         selected_index=1)]]
        print(f'Proceeding to scrape URLs for {scrape_position} for the year: '
              + '{scrape_year}')
        
    return scrape_position, scrape_year

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

def scrapePlayerStats(player, year, index, list_length, position):
    '''
    '''
    playerInfo = {}
    soup = soupifyURL(player['url'])
    
    playerInfo['url'] = player['url']
    playerInfo['position'] = player['position']
    
    # Find player ID and all remaining URLs we'll need
    url = soup.find('link', {'rel':'canonical'})['href'].split('profile')[0]
    
    ### Extract Basic Info
    try:
        playerInfo['name_first'] = soup.find(
                'span', {'class':'player-name'}).text.split(' ')[0].strip()
        playerInfo['name_last'] = soup.find(
                'span', {'class':'player-name'}).text.split(' ')[1].strip()
    except:
        return
    
    #--------------------------------------------------------------------------
    #---- Basic Player Information
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    #---- Situational Stats
    #--------------------------------------------------------------------------
    soup = soupifyURL(url + 'situationalstats?season=' + year)

    #--------------------------------------------------------------------------
    #---- Summarized Annual Statistics
    #--------------------------------------------------------------------------
    soup = soupifyURL(url + 'careerstats')
    
    print('Year ' + str(year) + ', Done with: ' + playerInfo['name_first'] + \
          ' ' + playerInfo['name_last'] + ' (Player ' + str(index) + \
          ' out of ' + str(list_length-1) + ')')
    return playerInfo

def scrapePlayerURL(soup, url_list):
    '''
    '''
    playerTable = soup.find('table', {'class':'data-table1'})
    # skip the table header info and go right to player info
    playerTbody = playerTable.find('tbody')
    #playerTbody = playerTable.find_all('tbody')[1]
    playerRows = playerTbody.find_all('tr')
    for row in playerRows:
        player = {}
        # set the URL for the player and their position
        player['url'] = ('http://www.nfl.com' + 
              row.find_all('td')[1].find('a', href=True)['href'])
        player['position'] = row.find_all('td')[3].text
        url_list.append(player)  
    return url_list

def compileExistingPlayers(path_position):
    '''
        Create a list of player urls for all .json files in the specified
        player folder. This reduces the need to players that are already on file
    '''
    path_position = Path(path_root, 'Data', 'PlayerStats', position)
    # Read in all player data from the available JSON files
    files = [f for f in os.listdir(path_position) 
                if f.endswith('.json') and len(f) > len(position+'.json')]
    files = sorted(files)
    
    player_list = []
    for file in files:
        with open(file, 'r') as f:
            jsonFile = json.load(f)
            for player in jsonFile:
                if player['url'] not in player_list:
                    player_list.append(player['url'])
    return player_list

def scrapePosition(year, position):
    '''
    '''   
    # Extract the original page information
    url = ('http://www.nfl.com/stats/categorystats?tabSeq=1&' +
           'statisticPositionCategory=' + position + '&season=' + year +
           '&seasonType=REG')
    soup = soupifyURL(url)
       
    # Extract the number of remaining pages for that position
    pages_html = soup.find('span', {'class':'linkNavigation floatRight'})
    page_url_list = []
    for page in pages_html.find_all('a', href=True)[:-1]:
        page_url_list.append('http://www.nfl.com' + page['href'])
    
    # Extract the links for every player within the given year by iterating
    #   across every page in the year
    # grab the first page
    player_url_list = []
    player_url_list = scrapePlayerURL(soup, player_url_list)
    # grab every subsequent page
    for url in page_url_list:
        soup = soupifyURL(url)
        player_url_list = scrapePlayerURL(soup, player_url_list)
       
    # Extract player information for every player within a year
    playerList = []
    for player in player_url_list:
        playerList.append(scrapePlayerStats(
                player, year, player_url_list.index(player), len(
                        player_url_list), position)) 
        
    # Export the data set as a JSON file
    #filename = '/' + position + '/' + year + '_' + position + '.json'
    filename = year + '_' + position + '.json'
    with open(filename, 'wt') as out:
        json.dump(playerList, out, sort_keys=True, indent=4, separators=(
                ',', ': '))
        
    # Convert the list to a Pandas dataframe, fill in missing values with 0, 
    #   and export the dataframe to a CSV file
#        df = pd.DataFrame(playerList)
#        df.fillna(0, inplace=True)
#        filename = year + '_' + position + '.csv'
#        df.to_csv(Path('Data', 'PlayerStats', position, filename), sep='\t', index=False)
    
#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
path_root = '/home/ejreidelbach/Projects/NFL'
os.chdir(path_root)
    
# Ask the user what positions and what years data should be scraped for
list_positions, list_years = askUserForInput()

# Scrape all positions for 2017
for position in tqdm.tqdm(list_positions):
    try:
        os.chdir(Path(path_root, 'Data', 'PlayerStats', position))
    except:
        os.makedirs(Path(path_root, 'Data', 'PlayerStats', position))
#    existing_players_list = compileExistingPlayers(
#            Path(path_root, 'Data', 'PlayerStats', position))
    for year in tqdm.tqdm(list_years):
        scrapePosition(year, position)