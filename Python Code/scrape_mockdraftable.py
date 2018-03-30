# coding: utf-8
#The goal of this notebook will be to scrape the combine data contained on (MockDraftable)[https://www.mockdraftable.com].
#
#Our first attempt at scraping the data will be to iterate through all position groups, grabbing player information as we go.  The way positions are stored on the site are very interesting.  They basic format is listed below:
#
#ATH (Athlete)
# |
# |__ SKILL (Skill Position Player)
# |     |
# |     |__ QB (Quarterback)
# |     |
# |     |__ BALL (Ball Carrier)
# |           |
# |           |__ RB (Running Back)
# |           |    |
# |           |    |__ FB (Fullback)
# |           |    |
# |           |    |__ HB (Halfback)
# |           |
# |           |__ WR (Wide Receiver)
# |           |
# |           |__ TE (Tight End)
# |           
# |__ OL (Offensive Line)
# |   |
# |   |__ OT (Offensive Tackle)
# |   | 
# |   |__ IOL (Interior Offensive Line)
# |        |
# |        |__ OG (Offensive Guard)
# |        |
# |        |__ OC (Offensive Center)
# |
# |__ ST (Special Teams)
# |
# |__ DL (Defensive Line)
# |   |
# |   |__ IDL (Interior Defensive Line)
# |   |    |
# |   |    |__ DT (Defensive Tackle)
# |   |
# |   |__ DE (One-Gap Defensive End)
# |
# |__ EDGE (Edge Defender)
# |
# |__ LB (Linebacker)
# |   |
# |   |__ OBLB (Off-Ball Linebacker)
# |         |
# |         |__ ILB (Inside Linebacker)
# |         |
# |         |__ OLB (Outside Linebacker)
# |
# |__ DB (Defensive Back)
#     |
#     |__ S (Safety)
#     |   |
#     |   |__ SS (Box/Strong Safety)
#     |   |
#     |   |__ FS (Deep/Free Safety)
#     |
#     |__ CB (Cornerback)

# Import necessary packages
import json
import pandas as pd
import os
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import time

def advancePage(browser):
    # Extract the navigation bar at the bottom of the page for navigation
    navBar = browser.find_elements_by_class_name('btn-group')
    
    # Advance to the next page by hitting the next button
    navBar[len(navBar)-1].click()    

def cleanUpData(player):
    for data in player:
        if player[data] == None:
            pass
        elif data in ['weight','combineBench']:
            player[data] = player[data].split(' ')[0]
        elif data in ['wingspan','lengthArm','lengthHand','combineBroad','combineVert']:
            player[data] = player[data].split('"')[0]
        elif data in ['combineCone','combine10split','combine20split','combine40dash','combine20shuttle','combine60shuttle']:
            player[data] = player[data].split('s')[0]
    return player

def createPlayerDict():
    varNames = ['nameFirst', 'nameLast', 'draftYear', 'college', 'heightFeet', 'heightInches','weight', 'wingspan', 
                'lengthArm', 'lengthHand', 'combine10split', 'combine20split', 'combine40dash', 'combineBench', 
                'combineVert', 'combineBroad', 'combineCone', 'combine20shuttle', 'combine60shuttle','url','position']
    playerDict = {}
    for var in varNames:
        playerDict[var] = None
    return playerDict

def fractionCheck(text):
    # For reference: https://www.compart.com/en/unicode/decomposition/%3Cfraction%3E
    fractions = [u"⅒",u"⅑",u"⅛",u"⅐",u"⅙",u"⅕",u"¼",u"⅓",u"⅜",u"⅖",u"½",u"⅗",u"⅝",u"⅔",u"¾",u"⅘",u"⅚",u"⅞"]
    fraction_values = [u".1",u".111",u".125",u".143",u".167",u".2",u".25",u".333",u".375",u".4",u".5",u".6",u".625",
                       u".666",u".75",u".8",u".833",u".875"]
    #for fraction in fractions:
    for a, b in zip(fractions, fraction_values):
        if a in text:
            return text.replace(a, b).encode('ascii','ignore').strip()      
    return text.encode('ascii','ignore').strip()

def getVariableName(name):
    variableDict = {'Height':'height', 'Weight':'weight', 'Wingspan':'wingspan', 'Arm Length':'lengthArm',
                    'Hand Size':'lengthHand', '10 Yard Split':'combine10split', '20 Yard Split':'combine20split',
                    '40 Yard Dash':'combine40dash', 'Bench Press':'combineBench', 'Vertical Jump':'combineVert',
                    'Broad Jump':'combineBroad', '3-Cone Drill':'combineCone', '20 Yard Shuttle':'combine20shuttle',
                    '60 Yard Shuttle':'combine60shuttle'}
    return(variableDict[name])

def makeURL(position):
    #baseURL = 'https://www.mockdraftable.com/search?position=QB&beginYear=1999&endYear=2018&sort=DESC&page='
    URL = 'https://www.mockdraftable.com/search?position=' + position + '&beginYear=1999&endYear=2018&sort=DESC&page=1'
    return URL

def pageNumberStatus(soup):
    selectedButton = soup.find_all('button',{'class':'btn btn-secondary active'})[-1]
    lastButton = soup.find_all('button',{'class':'btn btn-secondary'})[-2]
    return [int(selectedButton.text), int(lastButton.text)]

def retrievePlayerInfo(soup,url):
    # Initialize a player dictionary
    playerDict = createPlayerDict()

    # Set url and position
    playerDict['url'] = url
    playerDict['position'] = url.split('position=')[1]

    # Retrieve basic player information
    playerName = soup.find('div',{'class':'mb-0 mt-1 h3 align-bottom playerbar-name'}).text.encode('ascii','ignore').strip()
    playerDict['nameFirst'] = playerName.split(' ')[0]
    playerDict['nameLast'] = playerName.split(' ')[1]
    
    for dd in soup.find_all('dd'):
        playerDict['draftYear'] = dd[0].text.split('\n')[0]
        playerDict['college'] = dd[2].text.split('\n')[0]    

    # Retrieve player measurables
    measureablesTable = soup.find('tbody')
    rows = measureablesTable.find_all('tr')
    for row in rows:
        columns = row.find_all('td')
        keyName = getVariableName(str(columns[0].text))
        if keyName == 'height':
            playerDict['heightFeet'] = columns[1].text.encode('ascii', 'ignore').replace("\'","").split(' ')[0]
            playerDict['heightInches'] = columns[1].text.encode('ascii', 'ignore').replace("\'","").split(' ')[1].replace('"','')
        else:
            value = fractionCheck(columns[1].text)
            playerDict[keyName] = value

    # remove unnecessary formatting from measurable values
    playerDict = cleanUpData(playerDict)
    
    return playerDict

def retrievePlayerURL(soup,linkList):
    playerLinks = soup.find_all('a', {'class':'list-group-item list-group-item-action justify-content-between d-flex'})
    for link in playerLinks:
        linkList.append('https://www.mockdraftable.com' +link['href'])
    return linkList

def soupifyURL(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content,'lxml')
    return soup

# establish default header information
headers = {"User-agent":
           "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}

# create a list of all the positions we'll be scraping
positionList = ['QB','FB','HB','WR','TE','OT','OG','OC','ST','DT','DE','EDGE','ILB','OLB','SS','FS','CB']
player_URL_List = []

#  Use the instructions found here to install PhantomJS on Ubuntu:
#       https://www.vultr.com/docs/how-to-install-phantomjs-on-ubuntu-16-04

# Open a PhantomJS web browser and direct it to the DEA's dropbox search page
#browser = webdriver.PhantomJS()
#browser = webdriver.Firefox()
browser = webdriver.Firefox(executable_path=r'E:\Projects\geckodriver.exe')
browser.implicitly_wait(100)

# Iterate through every position we want to scrape
for position in positionList:
    # make the first version of the URL
    url = makeURL(position)
    browser.get(url)
    pageStatus = [0, 1]    
    print(position)
    
    # Iterate through every subsequent page in the position group
    while (pageStatus[0] < pageStatus[1]):
        soup = soupifyURL(browser.current_url)
        pageStatus = pageNumberStatus(soup)
        #print('Current Page: ' + str(pageStatus[0]) + ', Next Page: ' + str(pageStatus[1]))
        
        player_URL_List = retrievePlayerURL(soup, player_URL_List)

        # advance the page
        advancePage(browser)
        time.sleep(3)

playerList = []
urlCount = 0
for url in player_URL_List:
    soup = soupifyURL(url)
    print(url)
    playerList.append(retrievePlayerInfo(soup,url))
    if (urlCount%100==0): print(urlCount)
    urlCount+=1
