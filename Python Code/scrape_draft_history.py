#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 14:26:57 2018

@author: ejreidelbach

:DESCRIPTION:
    - This script will scrape the site: http://www.drafthistory.com/ in order 
    to obtain a complete listing of all players drafted in NFL history
    
:REQUIRES:
   
:TODO:
"""


 
#==============================================================================
# Package Import
#==============================================================================
import json
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import requests
import operator

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
def retrieveYearURL(soup,linkList):
    playerLinks = soup.find_all('a', {'class':'list-group-item list-group-item-action justify-content-between d-flex'})
    for link in playerLinks:
        linkList.append('https://www.mockdraftable.com' +link['href'])
    return linkList

def soupifyURL(url):
    r = requests.get(url, headers=headers)
#    soup = BeautifulSoup(r.content,'lxml')
    soup = BeautifulSoup(r.content,'html5lib')
    return soup

positionList = ['T','G','C']
positionAbbrList = ['OT','OG','OC']
#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/Combine')

# Set the link that we will be scraping
mainURL = r'http://www.drafthistory.com/index.php/years/'

# establish default header information
headers = {"User-agent":
           "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}

# Open a PhantomJS web browser and direct it to the DEA's dropbox search page
options = Options()
options.set_headless(headless=True)
browser = webdriver.Firefox(firefox_options=options)
#browser = webdriver.Firefox(executable_path=r'E:\Projects\geckodriver.exe')
browser.implicitly_wait(100)

# Scrape the main page and obtain a url for every year the NFl has had a draft
browser.get(mainURL)
    
# Iterate through every subsequent page in the position group
soup = soupifyURL(browser.current_url)
table = soup.find('table')

url_list = []
for row in table.find_all('td'):
    temp_dict = {}
    if (len(row.text) > 1):
        temp_dict['year'] = row.text
        temp_dict['url'] = row.find('a')['href']
        url_list.append(temp_dict)
        
# sort the url_list by year
url_list.sort(key=operator.itemgetter('year'))
        
# For all drafts from 1970 on, extract the information 
#   and add it to the overall list.
draft_list = []
for url in url_list[34:]:
    soup = soupifyURL(url['url'])

    #year_list = []   
    draft_round = ''
    # grab the year's data
    table = soup.find('table')
    for row in table.find_all('tr')[2:]:
        player_dict = {}
        cols = row.find_all('td')
        if cols[0].text != '\xa0':
            player_dict['round'] = cols[0].text
            draft_round = cols[0].text
        else:
            player_dict['round'] = draft_round
        player_dict['pick'] = cols[1].text
        player_dict['overall'] = cols[2].text
        player_dict['nameFirst'] = cols[3].text.split(' ')[0]
        player_dict['nameLast'] = cols[3].text.split(' ')[1]
        player_dict['team'] = cols[4].text
        for x,y in zip(positionList,positionAbbrList):
            if (x == cols[5].text):
                player_dict['position'] = y
            else:
                player_dict['position'] = cols[5].text
        player_dict['school'] = cols[6].text
        player_dict['year'] = url['year']
        
        # add the player's info to the list of all the year's picks
        #year_list.append(player_dict)
        
        # add the year's info to the historic list of all year's data
        draft_list.append(player_dict)
        
    print('Done with: ' + url['year'])
    
# Write the historic list to a .json file
filename = 'historic_draft_data.json'
with open(filename, 'wt') as out:
    json.dump(draft_list, out, sort_keys=True, indent=4, separators=(',', ': ')) 