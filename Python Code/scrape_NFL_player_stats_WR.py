#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 16 15:01:38 2018

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
import pandas as pd
import os
from bs4 import BeautifulSoup
import requests
import time

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
headers = {"User-agent":
           "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}

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
position_list = {'QUARTERBACK',
                 'RUNNING_BACK',
                 'WIDE_RECEIVER',
                 'TIGHT_END',
                 'DEFENSIVE_LINEMAN',
                 'LINEBACKER',
                 'DEFENSIVE_BACK',
                 'PUNTER',
                 'FIELD_GOAL_KICKER',
                 }

# years for which stats can be obtained
year_list = {'2017',
             '2016',
             '2015',
             '2014',
             '2013',
             '2012',
             '2011',
             '2010',
             '2009',
             '2008',
             '2007',
             '2006',
             '2005',
             '2004',
             '2003',
             '2002',
             '2001',
             '2000',
             '1999',
        }

# create a dictionary that determines stats to scrape for each position
scrape_dict = {'QB':['Passing Splits','Rushing Splits'],
               'RB':['Receiving Splits','Rushing Splits'],
               'WR':['Receiving Splits','Rushing Splits'],
               'TE':['Receiving Splits'],
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
scrape_dict_year = {'QB':['PASSING','RUSHING'],
                    'RB':['RECEIVING','RUSHING','PUNT RETURN','KICK RETURN'],
                    'WR':['RECEIVING','RUSHING','PUNT RETURN','KICK RETURN'],
                    'TE':['RECEIVING'],
                    'DE':['DEFENSIVE'],
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

def soupifyURL(url):
    r = requests.get(url, headers=headers)
#    soup = BeautifulSoup(r.content,'lxml')
    soup = BeautifulSoup(r.content,'html5lib')
    return soup

def scrapePlayerStats(url, year):   
    playerInfo = {}
    soup = soupifyURL(url)
    
    playerInfo['year'] = year
    playerInfo['url'] = url
    
    # Find player ID and all remaining URLs we'll need
    url = soup.find('link', {'rel':'canonical'})['href'].split('profile')[0]
    
    ### Extract Basic Info
    playerInfo['name_first'] = soup.find('span', {'class':'player-name'}).text.split(' ')[0].strip()
    playerInfo['name_last'] = soup.find('span', {'class':'player-name'}).text.split(' ')[1].strip()
    
    temp = list(soup.find('div', {'class':'player-info'}).find_all('p')[2])
    playerInfo['height'] = temp[2].split(': ')[1].strip()
    playerInfo['weight'] = temp[4].split(': ')[1].strip()
    playerInfo['age'] = temp[6].split(': ')[1].strip()
    
    temp = list(soup.find('div', {'class':'player-info'}).find_all('p')[4])
    playerInfo['college'] = temp[1].split(': ')[1].strip()
    
    playerInfo['pic_url'] = soup.find('div', {'class':'player-photo'}).find('img')['src']
    
    temp = list(soup.find('div', {'class':'player-info'}).find_all('p')[5])
    playerInfo['experience'] = temp[1].split(': ')[1][0]

    temp = list(soup.find('div', {'class':'player-info'}).find_all('p')[6])    
    playerInfo['high_school_state'] = temp[1].split('[')[1].split(']')[0]
    
    playerInfo['position'] = soup.find('span', {'class':'player-number'}).text.split(' ')[1].strip()
    playerInfo['team_current'] = soup.find('p', {'class':'player-team-links'}).find('a').text
    playerInfo['team_pic_url'] = soup.find('div', {'class':'player-photo'}).find('img')['src']
    
    ### Extract Situational Stats
    
    soup = soupifyURL(url + 'situationalstats')
    
    # Determine what stats are available for the player
    stat_split_list = []
    stat_splits = soup.find('ul', {'class':'player-tabs'})
    for stat_split in stat_splits.find_all('a'):
        stat_split_list.append(stat_split.text)

    # Extract stats for every category that is of interest to that position group
    for stat_split in stat_split_list:
        
        # If the stat category is worthy of scraping for that position, scrape it
        if stat_split in scrape_dict[playerInfo['position']]:
            
            # Find the stat tables for the specified split category
            temp_table = soup.find('div',{'id':'game_split_tabs_'+str(
                    stat_split_list.index(stat_split))}).find_all('table', {'class':'data-table1'})

            # If the returned tables are empty, skip to the next category
            if temp_table == []:
                continue
                
            # If the tables contain data for that split category, scrape them
            else:
                
                # Iterate through every stat category and extract out the data
                for table in temp_table:
                    # Get the stat category
                    cat = table.find('td',{'class':'first-td'}).text.lower().replace(' ','_')
                    
                    # Ignore the Attempts 
                    if cat == 'attempts' and stat_split == 'Receiving Splits':
                        continue
                    
                    # Get the category column headers
                    cat_stats_list = []
                    header = table.find('tr', {'class':'player-table-key'})
                    for col in header.find_all('td')[1:]:
                        cat_stats_list.append(col.text.lower()) 

                    # Extract the rows that have statistics to scrape              
                    values_list = list(table.find('tbody').find_all('tr'))
                    values_list = [i for i in values_list if len(i) > 1]   
                    
                    # For every row, merge the row header with the column header
                    #   to creat a variable name and extract the associated value
                    for value in values_list:
                        subcat = value.find('td').text.lower().replace(' ','_')
                        for stat, col  in zip(cat_stats_list, value.find_all('td')[1:]):
                            if (col.text == '--'):
                                playerInfo[stat_split.split(' ')[0].lower() + \
                                           '_' + cat + '_' + subcat + '_' + stat] = int(0)
                                continue
                            try:
                                playerInfo[stat_split.split(' ')[0].lower() + \
                                           '_' + cat + '_' + subcat + '_' + stat] = int(
                                           col.text.replace(',',''))
                            except:
                                playerInfo[stat_split.split(' ')[0].lower() + \
                                           '_' + cat + '_' + subcat + '_' + stat] = float(
                                           col.text.replace(',',''))        
  
    ### Extract Summarized Annual Statistics
    soup = soupifyURL(url + 'careerstats')

    # Determine what stats are available for the player
    year_stat_split_list = []
    year_stat_splits = soup.find_all('thead')
    for year_stat_split in year_stat_splits:
        year_stat_split_list.append(year_stat_split.find('div').text)

    # Set the player's team for that year
    year_team = soup.find('table', {'class':'data-table1'}).find('tbody').find('tr').find_all('td')[1].text.strip()
    playerInfo['team_' + year] = year_team

    # Extract stats for every category that is of interest to that position group
    for year_stat in year_stat_split_list:
        # If the stat category is worthy of scraping for that position, scrape it
        if year_stat.upper() in scrape_dict_year[playerInfo['position']]:
            
            # Find the stat tables for the specified split category
            temp_table = soup.find_all('table', {'class':'data-table1'})
            temp_table = temp_table[year_stat_split_list.index(year_stat)]
            
            # Extract the data for the specifed category
            
            cols = temp_table.find('thead').find_all('td')[3:]
            data = temp_table.find('tbody').find('tr').find_all('td')[2:]

            for col, dat in zip(cols, data):
                if (dat.text.strip() == '--'):
                    playerInfo[year + '_' + year_stat.replace(' ','_').lower() \
                               + '_' + col.text.lower()] = int(0)
                elif len(dat.text.strip()) > 6:
                    playerInfo[year + '_' + year_stat.replace(' ','_').lower() \
                               + '_' + col.text.lower()] = dat.text.strip()
                else:
                    try:
                        playerInfo[year + '_' + year_stat.replace(' ','_').lower() \
                                   + '_' + col.text.lower()] = int(
                                   dat.text.replace(',',''))
                    except:
                        playerInfo[year + '_' + year_stat.replace(' ','_').lower() \
                                   + '_' + col.text.lower()] = float(
                                   dat.text.replace(',',''))
    
    ### Extract Draft
    soup = soupifyURL(url + 'draft')
    temp = soup.find('div', {'id':'draft-basics'})
    try:
        playerInfo['draft_round'] = temp.find_all('p')[2].find('span', {'class':'round'}).text
        playerInfo['draft_pick_round'] = temp.find_all('p')[3].text.split(': ')[1].split(' ')[0]
        playerInfo['draft_pick_overall'] = temp.find_all('p')[0].text.split('Pick No.')[1]
        playerInfo['draft_team'] = temp.find_all('p')[1].find('span', {'class':'team'}).text   
    except:
        playerInfo['draft_round'] = ''
        playerInfo['draft_pick_round'] = ''
        playerInfo['draft_pick_overall'] = ''
        playerInfo['draft_team'] = ''
    
    ### Extract Combine
#    soup = soupifyURL(url + 'combine')
#    playerInfo['combine_20shuttle'] = ''
#    playerInfo['combine_60shuttle'] = ''
#    playerInfo['combine_40dash'] = ''
#    playerInfo['combine_bench'] = ''
#    playerInfo['combine_broad'] = ''
#    playerInfo['combine_cone'] = ''
#    playerInfo['combine_vert'] = ''
#    playerInfo['combine_height'] = ''
#    playerInfo['combine_lengthArm'] = ''
#    playerInfo['combine_lengthHand'] = ''
#    playerInfo['combine_weight'] = ''
    
    print('Done with: ' + playerInfo['name_first'] + ' ' + playerInfo['name_last'])
    return playerInfo

def scrapePlayerURL(soup, url_list):
    playerTable = soup.find('table', {'class':'data-table1'})
    # skip the table header info and go right to player info
    playerTbody = playerTable.find_all('tbody')[1]
    playerRows = playerTbody.find_all('tr')
    for row in playerRows:
        playerURL = row.find_all('td')[1].find('a', href=True)['href']
        url_list.append('http://www.nfl.com' + playerURL)  
    return url_list

def scrapeYearByPosition(year, position):
    # Extract the original page information
    url = ('http://www.nfl.com/stats/categorystats?tabSeq=1&season=' 
       + year + '&seasonType=REG&d-447263-p=1&statisticPositionCategory=' 
       + position)
    soup = soupifyURL(url)
       
    # Extract the number of remaining pages for that position
    pages_html = soup.find('span', {'class':'linkNavigation floatRight'})
    page_url_list = []
    for page in pages_html.find_all('a', href=True)[:-1]:
        page_url_list.append('http://www.nfl.com' + page['href'])
    
    # Extract the links for every player within the given year
    url_list = []
    url_list = scrapePlayerURL(soup, url_list)
    for url in page_url_list:
        soup = soupifyURL(url)
        url_list = scrapePlayerURL(soup, url_list)
       
    # Extract player information for every player within a year
    playerList = []
    for url in url_list:
        playerList.append(scrapePlayerStats(url,year)) 
        
    # Export the data set
    filename = year + '_' + position + '.json'
    with open(filename, 'wt') as out:
        json.dump(playerList, out, sort_keys=True, indent=4, separators=(',', ': '))

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/PlayerStats')

#for year in year_list:
#    for position in position_list:
#        scrapeYearByPosition(year,position)
scrapeYearByPosition('2017','WIDE_RECEIVER')