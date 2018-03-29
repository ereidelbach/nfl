# coding: utf-8
import json
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests

def scrape_player_links(pageHTML,linkList):
    soup = BeautifulSoup(pageHTML, 'lxml')
    playerTD = soup.findAll('td', {'class':'name selected'})
    for player in playerTD:
        link = player.find('a')['href'].encode('ascii','ignore').strip()
        linkList.append(link)
    return linkList

#  Use the instructions found here to install PhantomJS on Ubuntu:
#       https://www.vultr.com/docs/how-to-install-phantomjs-on-ubuntu-16-04

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

# Now that we have all the player links, we can access each individual player page to obtain detailed information.
playerInfoNames = ['pic_url','name_first','name_last','college','conference','position','hometown_city',
                   'hometown_state','class','height','weight','arms','hands','prospect_grade','combineID',
                   'combine_40','combine_bench','combine_vertical','combine_broad','combine_3cone',
                   'combine_20','combine_60']
playerInfoList = []
playerCount = 0

headers = {"User-agent":
           "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}

for link in urlList:
    r = requests.get(link, headers=headers)
    soup = BeautifulSoup(r.content,'lxml')

    # Basic info is react_id = 153
    #basicInfo = soup.find('div', {'data-reactid':'153'})
    basicInfo = soup.findAll('script')[5].text
    basicInfo = basicInfo.split('__INITIAL_DATA__ = ')[1]
    basicInfo = basicInfo.split(';\n  ')[0]
    basicInfo = basicInfo.encode('ascii','ignore')
    basicInfo = basicInfo.replace('\\"','')

    temp = json.loads(basicInfo)

    player = {}

    player['picURL'] = temp['instance']['prospect']['headshot']['asset']['url']                  # pictureURL
    player['nameFirst'] = temp['instance']['prospect']['person']['firstName']                    # first name
    player['nameLast'] = temp['instance']['prospect']['person']['lastName']                      # last name
    player['college'] = temp['instance']['prospect']['currentCollege']                           # college
    player['conference'] = temp['instance']['prospect']['collegeConference']                     # conference
    player['position'] = temp['instance']['prospect']['position']                                # position
    player['homeCity'] = temp['instance']['prospect']['person']['hometown']                      # hometown-city
    player['homeState'] = temp['instance']['prospect']['homeState']                              # hometown-state
    player['schoolYear'] = temp['instance']['prospect']['collegeClass']                          # year of school
    player['height'] = temp['instance']['prospect']['height']                                    # height
    player['weight'] = temp['instance']['prospect']['weight']                                    # weight
    player['lengthArm'] = temp['instance']['prospect']['armLength']                              # arm length
    player['lengthHand'] = temp['instance']['prospect']['handSize']                              # hand length
    player['grade'] = temp['instance']['prospect']['grade']                                      # prospect grade
    player['combineID'] = temp['instance']['prospect']['combineData']['combineNumber']           # combine ID
    player['combine40'] = temp['instance']['prospect']['combineData']['fortyYardDashResult']     # 40 yard dash
    player['combineBench'] = temp['instance']['prospect']['combineData']['benchResult']          # bench press
    player['combineVert'] = temp['instance']['prospect']['combineData']['verticalJumpResult']    # vertical jump
    player['combineBroad'] = temp['instance']['prospect']['combineData']['broadJumpResult']      # broad jump
    player['combineCone'] = temp['instance']['prospect']['combineData']['threeConeDrillResult']  # 3 Cone Drill
    player['combine20'] = temp['instance']['prospect']['combineData']['twentyYardShuttleResult'] # 20 yard shuttle run
    player['combine60'] = temp['instance']['prospect']['combineData']['sixtyYardShuttleResult']  # 60 yard shuttle run
    player['overview'] = temp['instance']['prospect']['overview']                                # player Overview
    player['sources'] = temp['instance']['prospect']['sourcesTellUs']                            # info from sources
    player['strengths'] = temp['instance']['prospect']['strengths']                              # player strengths
    player['weaknesses'] = temp['instance']['prospect']['weaknesses']                            # player weaknesses
    player['bottomLine'] = temp['instance']['prospect']['bottomLine']                            # player bottom-line
    player['nflComp'] = temp['instance']['prospect']['nflComparison']                            # NFL comparison
    player['projection'] = temp['instance']['prospect']['draftProjection']                       # projected draft status
    player['profileAuthor'] = temp['instance']['prospect']['profileAuthor']                      # Profile Author

    playerInfoList.append(player)
    playerCount+=1
    if (playerCount%25==0): print(playerCount)

# Some values for hometown-City capture the state as well (let's fix this)
for player in playerInfoList:
    if (isinstance(player['homeCity'], basestring)):
        if ', ' in  player['homeCity']:
            oldCity = player['homeCity']
            player['homeCity'] = oldCity.split(', ')[0]
            player['homeState'] = oldCity.split(', ')[1]

# Export the data set
filename = 'combine_2018.json'
with open(filename, 'wt') as out:
    json.dump(playerInfoList, out, sort_keys=True, indent=4, separators=(',', ': '))
