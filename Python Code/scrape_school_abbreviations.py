#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 09:48:38 2018

@author: ejreidelbach

:DESCRIPTION: 
    - Colleges/Universities have very different combinations of names/abbreviations
    - This program will attempt to compile a list of these for future lookup
    and standardizartion purposes
    - The link will begin by utilizing the list found on:
        https://www.reddit.com/r/CFB/wiki/abbreviations

:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import os  
from bs4 import BeautifulSoup
import requests
import pandas as pd

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
def soupifyURL(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content,'html5lib')
    return soup

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/Data/')

# establish default header information
headers = {"User-agent":
           "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}

soup = soupifyURL('https://www.reddit.com/r/CFB/wiki/abbreviations')
table = soup.find_all('table')[1] 
df = pd.read_html(str(table))[0]

# expand columns that have more than one value to two columns
df['Abbreviation1'], df['Abbreviation2'] = df['Abbreviation'].str.split(' or ',1).str

# remove the original `Abbreviation` column
df = df.drop('Abbreviation', 1)

# remove conference rows from table
#df.dropna(inplace=True)

# write file to a csv
df.to_csv('school_abbreviations.csv', index=False)