#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 16 15:01:38 2018

@author: ejreidelbach

:DESCRIPTION:
    - This script will scrape player historical data from NFL.com
    
:REQUIRES:
   - Selenium
    
:TODO:
    - Expand beyond the WR position to capture player data for all positions
"""
 
#==============================================================================
# Package Import
#==============================================================================
import json
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
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
pass_stats_list = ['att',
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

rush_stats_list = ['att',
                   'yds',
                   'avg',
                   'lng',
                   'td',
                   '1st',]

rec_stats_list = ['rec',
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

# positions for which stats can be obtained
position_list = {'QUARTERBACK',
                 'RUNNING_BACK',
                 'WIDE_RECEIVER',
                 'TIGHT_END',
                 'DEFENSIVE_LINEMAN',
                 'LINEBACKER',
                 'DEFENSIVE_BACK',
                 'KICKOFF_KICKER',
                 'KICK_RETURNER',
                 'PUNTER',
                 'PUNT_RETURNER',
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
scrape_dict = {'QUARTERBACK':['Passing Splits','Rushing Splits'],
               'RUNNING_BACK':['Receiving Splits','Rushing Splits'],
               'WIDE_RECEIVER':['Receiving Splits','Rushing Splits'],
               'TIGHT_END':'',
               'DEFENSIVE_LINEMAN':'',
               'LINEBACKER':'',
               'DEFENSIVE_BACK':'',
               'KICKOFF_KICKER':'',
               'KICK_RETURNER':'',
               'PUNTER':'',
               'PUNT_RETURNER':'',
               'FIELD_GOAL_KICKER':'',
              }

def soupifyURL(url):
    r = requests.get(url, headers=headers)
#    soup = BeautifulSoup(r.content,'lxml')
    soup = BeautifulSoup(r.content,'html5lib')
    return soup

def scrapePlayerStats(url, year, browser):
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
    playerInfo['team'] = soup.find('p', {'class':'player-team-links'}).find('a').text
    playerInfo['team_pic_url'] = soup.find('div', {'class':'player-photo'}).find('img')['src']
    
    ### Extract Situational Stats
    
    soup = soupifyURL(url + 'situationalstats')
    temp_table = soup.find_all('table', {'class':'data-table1'})
    if temp_table == []:
        for stat in stats_all:
            for cat in rec_stats_list:
                playerInfo[stat + '_' + cat] = ''
    else:
        # Get column headers
        cat_stats_list = []
        header = temp_table[0].find('tr', {'class':'player-table-key'})
        for col in header.find_all('td')[1:]:
            cat_stats_list.append(col.text.lower())
        
        # Determine what stats are available for the player
        split_url_list = ''
        Skipping Rushing / Passing / Defensive for WR
    
        # Calculate Yearly Stats
    
        # Extract Receiving Splits for WR
        ## Attempts (SKIPPED - Not relavant for WR)
        temp = temp_table[0]
        playerInfo['stats_attempts_1_10']
        
        ## Field Position ############################################      
        values_list = list(temp_table[-7].find('tbody').find_all('tr'))
        values_list = [i for i in values_list if len(i) > 1]   
        
        for stat, value in zip(stats_field, values_list):
            for cat, col  in zip(cat_stats_list, value.find_all('td')[1:]):
                if (col.text == '--'):
                    playerInfo[stat + '_' + cat] = int(0)
                try:
                    playerInfo[stat + '_' + cat] = int(col.text.replace(',',''))
                except:
                    playerInfo[stat + '_' + cat] = float(col.text.replace(',',''))
        
        ## Half ######################################################
        values_list = list(temp_table[-6].find('tbody').find_all('tr'))
        values_list = [i for i in values_list if len(i) > 1]
        
        for stat, value in zip(stats_half, values_list):
            for cat, col  in zip(cat_stats_list, value.find_all('td')[1:]):
                try:
                    playerInfo[stat + '_' + cat] = int(col.text.replace(',',''))
                except:
                    playerInfo[stat + '_' + cat] = float(col.text.replace(',',''))
        
        ## Home/Away #################################################
        values_list = list(temp_table[-5].find('tbody').find_all('tr'))
        values_list = [i for i in values_list if len(i) > 1]

        for stat, value in zip(stats_home_away, values_list):
            for cat, col  in zip(cat_stats_list, value.find_all('td')[1:]):
                try:
                    playerInfo[stat + '_' + cat] = int(col.text.replace(',',''))
                except:
                    playerInfo[stat + '_' + cat] = float(col.text.replace(',',''))
        
        ## Margin ####################################################
        values_list = list(temp_table[-4].find('tbody').find_all('tr'))
        values_list = [i for i in values_list if len(i) > 1]

        for stat, value in zip(stats_margin, values_list):
            for cat, col  in zip(cat_stats_list, value.find_all('td')[1:]):
                try:
                    playerInfo[stat + '_' + cat] = int(col.text.replace(',',''))
                except:
                    playerInfo[stat + '_' + cat] = float(col.text.replace(',',''))
        
        ## Point Situation ###########################################
        values_list = list(temp_table[-3].find('tbody').find_all('tr'))
        values_list = [i for i in values_list if len(i) > 1]

        for stat, value in zip(stats_points, values_list):
            for cat, col  in zip(cat_stats_list, value.find_all('td')[1:]):
                try:
                    playerInfo[stat + '_' + cat] = int(col.text.replace(',',''))
                except:
                    playerInfo[stat + '_' + cat] = float(col.text.replace(',',''))
        
        ## Quarters ##################################################
        values_list = list(temp_table[-2].find('tbody').find_all('tr'))
        values_list = [i for i in values_list if len(i) > 1]

        for stat, value in zip(stats_quarters, values_list):
            for cat, col  in zip(cat_stats_list, value.find_all('td')[1:]):
                try:
                    playerInfo[stat + '_' + cat] = int(col.text.replace(',',''))
                except:
                    playerInfo[stat + '_' + cat] = float(col.text.replace(',',''))
        
        ## Field Type ################################################
        values_list = list(temp_table[-1].find('tbody').find_all('tr'))
        values_list = [i for i in values_list if len(i) > 1]

        for stat, value in zip(stats_field_type, values_list):
            for cat, col  in zip(cat_stats_list, value.find_all('td')[1:]):
                try:
                    playerInfo[stat + '_' + cat] = int(col.text.replace(',',''))
                except:
                    playerInfo[stat + '_' + cat] = float(col.text.replace(',',''))
    
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
    soup = soupifyURL()
       
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
    
    # Open a Headless Firefox browser
    options = Options()
    options.set_headless(headless=True)
    browser = webdriver.Firefox(firefox_options=options)
    #browser = webdriver.Firefox(executable_path=r'E:\Projects\geckodriver.exe')
    browser.implicitly_wait(100)
    browser.get(url)    
    
    # Extract player information for every player within a year
    playerList = []
    for url in url_list[196:]:
        playerList.append(scrapePlayerStats(url,year, browser)) 
        
    # Export the data set
    filename = year + '_' + position + '.json'
    with open(filename, 'wt') as out:
        json.dump(playerList, out, sort_keys=True, indent=4, separators=(',', ': '))
        
    # Close the browser
    browser.quit()

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/PlayerStats')

#for year in year_list:
#    for position in position_list:
#        scrapeYearByPosition(year,position)
scrapeYearByPosition('2017','WIDE_RECEIVER')