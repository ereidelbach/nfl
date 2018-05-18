#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 16 15:01:38 2018

@author: ejreidelbach

:DESCRIPTION:
    - This script will scrape player historical data from NFL.com
    
:REQUIRES:
   - Selenium
   - PhantomJS headless browser: 
       Use the instructions found here to install PhantomJS on Ubuntu:
       https://www.vultr.com/docs/how-to-install-phantomjs-on-ubuntu-16-04
    
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
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
headers = {"User-agent":
           "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}

    
def scrape_player_links(pageHTML,linkList):
    soup = BeautifulSoup(pageHTML, 'lxml')
    playerTD = soup.findAll('td', {'class':'name selected'})
    for player in playerTD:
        link = player.find('a')['href'].encode('ascii','ignore').strip()
        linkList.append(link)
    return linkList

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects')

# Open a PhantomJS web browser and direct it to the DEA's dropbox search page
browser = webdriver.PhantomJS()
browser.get('http://www.nfl.com/combine/tracker#day=fullresults')
browser.implicitly_wait(100)

# Storage container for all player links
urlList = []

# Extract the original page information
html = browser.page_source
urlList = scrape_player_links(html, urlList)

# Extract the navigation bar at the bottom of the page for navigation
navBar = browser.find_elements_by_class_name('page')
pageCount = len(navBar)

# Advance to the next page (page 2)
buttons = browser.find_elements_by_class_name('page')
buttons[1].click()

# Advance to the next page and repeat the scraping process (for all remaining pages)
for page in range(2,pageCount):
    html = browser.page_source
    urlList = scrape_player_links(html,urlList)
    buttons = browser.find_elements_by_class_name('page')
    buttons[page].click()

# Grab the last page (since the loop won't iterate through the final page)
html = browser.page_source
urlList = scrape_player_links(html,urlList)

for link in urlList:
    r = requests.get(link, headers=headers)
    soup = BeautifulSoup(r.content,'lxml')

    playerInfoList.append(player)
    playerCount+=1
    if (playerCount%25==0): print(playerCount)

# Export the data set
filename = 'combine_2018.json'
with open(filename, 'wt') as out:
    json.dump(playerInfoList, out, sort_keys=True, indent=4, separators=(',', ': '))