#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 16:15:31 2018

@author: ejreidelbach

:DESCRIPTION:
    - This script will scrape player historical data from NFL.com
    
:REQUIRES:
    
:TODO:
    - Account for additional column header in kicker information regarding
        yardage kicks were attempted from
        ** example page: http://www.nfl.com/player/gregzuerlein/2534797/careerstats
"""
 
#==============================================================================
# Package Import
#==============================================================================
import json
import os
import requests
import tqdm

from bs4 import BeautifulSoup
from pathlib import Path

#==============================================================================
# Reference Variable Declaration
#==============================================================================
headers = {"User-agent":
           "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "\
           "(KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}
    

# categories for various statistics
stats_field = ['stats_field_pos_opp_19_to_1',
               'stats_field_pos_opp_49_to_20',
               'stats_field_pos_own_19_to_1',
               'stats_field_pos_own_21_to_50',]
stats_half = ['stats_first_half',
              'stats_second_half',
              'stats_last_two_min_half',]
stats_home_away = ['stats_home_games',
                   'stats_road_games',]    
stats_margin = ['stats_margin_0_to_7',
                'stats_margin_8_to_14',
                'stats_margin_15_plus',]
stats_points = ['stats_points_ahead',
                'stats_points_ahead_by_1_to_8',
                'stats_points_ahead_by_9_to_16',
                'stats_points_behind',
                'stats_points_behind_by_1_to_8',
                'stats_points_behind_by_9_to_16',
                'stats_points_tied',]
stats_quarters = ['stats_quarter_first',
                  'stats_quarter_second',
                  'stats_quarter_third',
                  'stats_quarter_fourth',
                  'stats_quarter_fourth_within_7',]
stats_field_type = ['stats_field_grass',
                    'stats_field_turf',]
stats_all = stats_field + stats_half + stats_home_away + stats_margin + \
            stats_points + stats_quarters + stats_field

# stat columns specific to the various categories
qb_stats_list = ['att',
                 'comp',
                 'pct',
                 'yds',
                 'avg',
                 'lng',
                 'td',
                 'int',
                 '1st',
                 '1st%',
                 '20+',
                 'sack',
                 'rate',]

rb_stats_list = ['att',
                 'yds',
                 'avg',
                 'lng',
                 'td',
                 '1st',]

wr_stats_list = ['rec',
                 'yds',
                 'avg',
                 'lng',
                 'td',
                 '1st',
                 '1st%',
                 '20+',
                 '40+',]

def_stats_list = ['comb',
                  'total',
                  'ast',
                  'sack',
                  'sfty',
                  'pdef',
                  'int',
                  'td',
                  'yds',
                  'avg',
                  'lng',]

kick_stats_list = ['20_29_att',
                   '20_29_made',
                   '30-39_att',
                   '30_39_made',
                   '40_49_att',
                   '40_49_made',
                   '50_+_att',
                   '50_+_made',
                   'fg_made',
                   'fg_att',
                   'fg_pct',]

punt_stats_list = []

# positions for which stats can be obtained
position_list = ['QUARTERBACK',
                 'RUNNING_BACK',
                 'WIDE_RECEIVER',
                 'TIGHT_END',
                 'DEFENSIVE_LINEMAN',
                 'LINEBACKER',
                 'DEFENSIVE_BACK',
#                 'PUNTER',
#                 'FIELD_GOAL_KICKER',
                 ]

# positions for which stats can be obtained
position_dict = {'QUARTERBACK':'QB',
                 'RUNNING_BACK':'RB',
                 'WIDE_RECEIVER':'WR',
                 'TIGHT_END':'TE',
                 'DEFENSIVE_LINEMAN':'DL',
                 'LINEBACKER':'LB',
                 'DEFENSIVE_BACK':'DB',
                 'PUNTER':'P',
                 'FIELD_GOAL_KICKER':'K',
                 }

# create a dictionary that determines stats to scrape for each position
scrape_dict = {'QB':['Passing Splits','Rushing Splits'],
               'RB':['Receiving Splits','Rushing Splits'],
               'HB':['Receiving Splits','Rushing Splits'],
               'FB':['Receiving Splits','Rushing Splits'],
               'WR':['Receiving Splits','Rushing Splits'],
               'TE':['Receiving Splits'],
               'DL':['Defensive Splits'],
               'DE':['Defensive Splits'],
               'DT':['Defensive Splits'],
               'NT':['Defensive Splits'],
               'ILB':['Defensive Splits'],
               'OLB':['Defensive Splits'],
               'MLB':['Defensive Splits'],
               'LB':['Defensive Splits'],
               'FS':['Defensive Splits'],
               'SS':['Defensive Splits'],
               'SAF':['Defensive Splits'],
               'CB':['Defensive Splits'],
               'DB':['Defensive Splits'],
               'P':['Punting Splits'],
               'K':['Kicking Splits'],
              }
# create a dictionary that determines stats to scrape for each position
#   for year-based statistics
scrape_dict_year = {'QB':['PASSING','RUSHING','FUMBLES'],
                    'RB':['RECEIVING','RUSHING','PUNT RETURN',
                          'KICK RETURN','FUMBLES'],
                    'HB':['RECEIVING','RUSHING','PUNT RETURN',
                          'KICK RETURN','FUMBLES'],
                    'FB':['RECEIVING','RUSHING','PUNT RETURN',
                          'KICK RETURN','FUMBLES'],
                    'WR':['RECEIVING','RUSHING','PUNT RETURN',
                          'KICK RETURN','FUMBLES'],
                    'TE':['RECEIVING','FUMBLES'],
                    'DE':['DEFENSIVE'],
                    'DL':['DEFENSIVE'],
                    'DT':['DEFENSIVE'],
                    'NT':['DEFENSIVE'],
                    'ILB':['DEFENSIVE'],
                    'OLB':['DEFENSIVE'],
                    'MLB':['DEFENSIVE'],
                    'LB':['DEFENSIVE'],
                    'FS':['DEFENSIVE'],
                    'SS':['DEFENSIVE'],
                    'SAF':['DEFENSIVE'],
                    'CB':['DEFENSIVE','PUNT RETURN','KICK RETURN'],
                    'DB':['DEFENSIVE','PUNT RETURN','KICK RETURN'],
                    'P':['PUNTING STATS','KICKOFF STATS'],
                    'K':['FIELD GOAL KICKERS','KICKOFF STATS'],
                    } 

#==============================================================================
# Function Definitions
#==============================================================================
def soupifyURL(url):
    '''
    '''
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content,'html.parser')
    return soup

def scrapePlayerStats(player, year, index, list_length, position):
    '''
    '''
#for player in player_url_list:
#    year = 2001
#    index = player_url_list.index(player)
#    list_length = len(player_url_list)
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
    
    # Check to see if a player is no longer active (if so, handle differently)
    temp = list(soup.find('div', {'class':'player-info'}).find_all('p'))
    if len(temp) <= 5 or (len(temp)==6 and temp[5].text.split(
            ':')[0] == 'Hall of Fame Induction'):
        temp = list(soup.find('div', {'class':'player-info'}).find_all('p')[1])
        height = temp[2].split(': ')[1].strip()
        playerInfo['height'] = height
        playerInfo['heightInches'] = int(height.split('-')[0])*12 + int(
                height.split('-')[1])
        playerInfo['weight'] = temp[4].split(': ')[1].strip()
        
        temp = list(soup.find('div', {'class':'player-info'}).find_all('p')[2])
        playerInfo['birthday'] = temp[2].split(' ')[1]
        
        
        temp = list(soup.find('div', {'class':'player-info'}).find_all('p')[3])
        playerInfo['college'] = temp[1].split(': ')[1].strip()
        playerInfo['pic_url'] = soup.find(
                'div', {'class':'player-photo'}).find('img')['src']
        
        playerInfo['team_current'] = 'INACTIVE'
#        playerInfo['team_pic_url'] = 'N/A'
        playerInfo['high_school_state'] = 'N/A'

    else:   
        temp = list(soup.find('div', {'class':'player-info'}).find_all('p')[2])
        height = temp[2].split(': ')[1].strip()
        playerInfo['height'] = height
        playerInfo['heightInches'] = int(height.split('-')[0])*12 + int(
                height.split('-')[1])
        playerInfo['weight'] = temp[4].split(': ')[1].strip()
        
        temp = list(soup.find('div', {'class':'player-info'}).find_all('p')[3])
        playerInfo['birthday'] = temp[2].split(' ')[1]
        
        temp = list(soup.find('div', {'class':'player-info'}).find_all('p')[4])
        playerInfo['college'] = temp[1].split(': ')[1].strip()
        
        playerInfo['pic_url'] = soup.find(
                'div', {'class':'player-photo'}).find('img')['src']
    
        try:
            temp = list(soup.find(
                    'div', {'class':'player-info'}).find_all('p')[6])    
            temp = temp[1].split('[')[1].split(']')[0]
            if ', ' in temp:
                temp = temp.split(', ')[1]
            elif ',' in temp:
                temp = temp.split(',')[1]
            playerInfo['high_school_state'] = temp
        except:
            playerInfo['high_school_state'] = 'N/A'
        
        playerInfo['team_current'] = soup.find(
                'p', {'class':'player-team-links'}).find('a').text
#        playerInfo['team_pic_url'] = soup.find(
#                'div', {'class':'player-photo'}).find('img')['src']
    
    ### Extract Situational Stats for every year available
    soup = soupifyURL(url + 'situationalstats')
    
    # Determine what years are available for the player
    try:
        year_soup = list(soup.find('select',{'id':'season'}).find_all('option'))
        stat_split_year_list = []
        for yr in year_soup:
            stat_split_year_list.append(yr.text)
            
        # Scrape stats for every available year
        situational_stats_list = []
        for scrape_year in stat_split_year_list:
        
            yearPlayerInfo = {}
            yearPlayerInfo['year'] = scrape_year
            
            soup = soupifyURL(url + 'situationalstats?season=' + scrape_year)
            
            # Determine what stats are available for the player
            stat_split_list = []
            stat_splits = soup.find('ul', {'class':'player-tabs'})
            for stat_split in stat_splits.find_all('a'):
                stat_split_list.append(stat_split.text)
        
            # Extract stats for every category that is of interest to that position
            for stat_split in stat_split_list:
                
                # Scrape a stat category if it's worthy of scraping for a position
                if stat_split in scrape_dict[playerInfo['position']]:
                    
                    # Find the stat tables for the specified split category
                    temp_table = soup.find('div',{'id':'game_split_tabs_'+str(
                            stat_split_list.index(stat_split))}).find_all(
                                        'table', {'class':'data-table1'})
        
                    # If the returned tables are empty, skip to the next category
                    if temp_table == []:
                        continue
                        
                    # If the tables contain data for that split category, scrape them
                    else:
                        
                        # Iterate through every stat category and extract out the data
                        for table in temp_table:
                            # Get the stat category
                            cat = table.find(
                                    'td',{'class':'first-td'}).text.lower().replace(
                                            ' ','_')
                            
                            # Ignore the Attempts 
                            if cat == 'attempts' and stat_split == 'Receiving Splits':
                                continue
                            
                            # Get the category column headers
                            cat_stats_list = []
                            header = table.find('tr', {
                                    'class':'player-table-key'})
                            for col in header.find_all('td')[1:]:
                                cat_stats_list.append(col.text.lower()) 
        
                            # Extract the rows that have statistics to scrape              
                            values_list = list(table.find('tbody').find_all('tr'))
                            values_list = [i for i in values_list if len(i) > 1]   
                            
                            # For every row, merge the row header with the column 
                            #   header to creat a variable name and extract the 
                            #   associated value
                            for value in values_list:
                                subcat = value.find('td').text.lower().replace(
                                        ' ','_')
                                for stat, col  in zip(
                                        cat_stats_list, value.find_all('td')[1:]):
                                    if (col.text == '--'):
                                        yearPlayerInfo[stat_split.split(
                                                ' ')[0].lower() + \
                                                   '_' + cat + '_' + \
                                                   subcat + '_' + stat] = int(0)
                                        continue
                                    try:
                                        yearPlayerInfo[stat_split.split(
                                                ' ')[0].lower() + \
                                                   '_' + cat + '_' + subcat + \
                                                   '_' + stat] = int(
                                                col.text.replace('T','').replace(
                                                        ',',''))
                                    except:
                                        yearPlayerInfo[stat_split.split(
                                                ' ')[0].lower() + \
                                            '_' + cat + '_' + subcat + \
                                            '_' + stat] = float(
                                                col.text.replace('T','').replace(
                                                        ',',''))     
            situational_stats_list.append(yearPlayerInfo)
        playerInfo['stats_situational'] = situational_stats_list
    except:
        pass

    ### Extract Summarized Annual Statistics
    soup = soupifyURL(url + 'careerstats')

    # Determine what years are available for the player
    try:
        years_list  = list(soup.find(
                'table', {'class':'data-table1'}).find('tbody').find_all('tr'))
        # remove any rows which do not contain statistical information
        for yr in years_list:
            if len(yr) == 1:
                years_list.remove(yr)
        # remove the Totals row
        del years_list[-1]
        year_count = len(years_list)
    except:
        years_list = []
   
    # If the returned tables are empty, the player has no career stats and we'll
    #   skip this section
    if len(years_list) == 0:
        playerInfo['stats_annual'] = []
        pass
    else:  
        # Determine what stats are available for the player
        year_stat_split_list = []
        year_stat_splits = soup.find_all('thead')

        
        # Determine what statistics are listed for a player
        for year_stat_split in year_stat_splits:
            year_stat_split_list.append(year_stat_split.find('div').text)
       
        # Extract stats for every category that are of interest based on the 
        #   player's position for all years that the playered has statistics
        career_stats_list = []
        for i in range(0,year_count):
            yearPlayerInfo = {}
            
            # set the year for which statistics will be scraped
            yearPlayerInfo['year'] = soup.find('table', {
                    'class':'data-table1'}).find('tbody').find_all('tr')[i*2]\
                    .find_all('td')[0].text.strip()
            
            # Set the player's team for that year
            yearPlayerInfo['team'] = soup.find('table', {
                    'class':'data-table1'}).find('tbody').find_all('tr')[i*2]\
                    .find_all('td')[1].text.strip()
                    
            # Iterate over every statistical category
            for year_stat in year_stat_split_list:                
                # If the stat category is worthy of scraping for that position,
                #   scrape it
                if year_stat.upper() in scrape_dict_year[playerInfo['position']]:
                    
                    # Find the stat tables for the specified split category
                    temp_table = soup.find_all('table', {'class':'data-table1'})
                    temp_table = temp_table[year_stat_split_list.index(year_stat)]
                    
                    # Extract the data for the specifed category                   
                    cols = temp_table.find('thead').find_all('td')[3:]
                    data = temp_table.find(
                            'tbody').find_all('tr')[i*2].find_all('td')[2:]
        
                    for col, dat in zip(cols, data):
                        if (dat.text.strip() == '--'):
                            yearPlayerInfo[year_stat.replace(' ','_').lower() \
                                       + '_' + col.text.lower()] = int(0)
                        elif len(dat.text.strip()) > 6:
                            yearPlayerInfo[year_stat.replace(' ','_').lower() \
                                       + '_' + col.text.lower()] = dat.text.strip()
                        else:
                            try:
                                yearPlayerInfo[year_stat.replace(
                                        ' ','_').lower() \
                                           + '_' + col.text.lower()] = int(
                                           dat.text.replace(
                                                   'T','').replace(',',''))
                            except:
                                yearPlayerInfo[year_stat.replace(
                                        ' ','_').lower() \
                                           + '_' + col.text.lower()] = float(
                                           dat.text.replace(
                                                   'T','').replace(',',''))
            career_stats_list.append(yearPlayerInfo)
        playerInfo['stats_annual'] = career_stats_list
    
    ### Extract Draft
    soup = soupifyURL(url + 'draft')
    temp = soup.find('div', {'id':'draft-basics'})
    try:
        playerInfo['draft_round'] = temp.find_all(
                'p')[2].find('span', {'class':'round'}).text
        playerInfo['draft_pick_round'] = temp.find_all(
                'p')[3].text.split(': ')[1].split(' ')[0]
        playerInfo['draft_pick_overall'] = temp.find_all(
                'p')[0].text.split('Pick No.')[1]
        playerInfo['draft_team'] = temp.find_all(
                'p')[1].find('span', {'class':'team'}).text   
    except:
        playerInfo['draft_round'] = 'N/A'
        playerInfo['draft_pick_round'] = 'N/A'
        playerInfo['draft_pick_overall'] = 'N/A'
        playerInfo['draft_team'] = 'Undrafted'
    
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
    
def scrapeNewYearByPosition(startYear, stopYear, position):
    '''
        Ingest 
    '''

def scrapeYearByPosition(startYear, stopYear, position, url_history_list):
    '''
    '''            
    years_to_scrape_list = list(range(stopYear,startYear-1,-1))
    # for every year specified, scrape the desired statistics
    for year in years_to_scrape_list:
        # convert the year from int to str for ease of reference     
        year = str(year)
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
            if player['url'] not in url_history_list:
                url_history_list.append(player['url'])
                playerList.append(scrapePlayerStats(
                        player, year, player_url_list.index(player), len(
                                player_url_list), position)) 
            else:
                print('Year ' + str(year) + ', Already read in: ' + 
                      player['url'].split('players/')[1].split('/')[0] + 
                      ' (Player ' +  str(player_url_list.index(player)) + 
                      ' out of ' + str(len(player_url_list)-1) + ')')
            
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
    
# Scrape all positions for 2017
#for position in position_list:
for position in tqdm.tqdm(position_list):
    try:
        os.chdir(Path(path_root, 'Data', 'PlayerStats', position))
    except:
        os.makedirs(Path(path_root, 'Data', 'PlayerStats', position))
    existing_players_list = compileExistingPlayers(
            Path(path_root, 'Data', 'PlayerStats', position))
    scrapeYearByPosition(2018, 2018, position, existing_players_list)