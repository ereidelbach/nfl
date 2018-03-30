#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 13:07:16 2018

@author: ejreidelbach

:DESCRIPTION:
    - This script will transfer the contents of the PFF 2018 NFL Draft Guide PDF
    into a .JSON file.

:REQUIRES:  
    - PyPDF2
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import os  
import PyPDF2

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL/')

# Begin reading the PDF file
# Instructions obtained from: https://automatetheboringstuff.com/chapter13/
pdfFileObj = open('Data/draft-guide2018.pdf', 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
pdfReader.numPages

# Extract PFF Position Rankings
rankingPageDict = {'QB':4, 'RB':26, 'WR':47, 'TE':87, 'OT':103, 'OG':125,
                   'OC':142, 'CB':156, 'S':184, 'LB':208, 'DT':242, 'DE':274}

pageObj = pdfReader.getPage(5)
page = pageObj.extractText()

page.split('\n')

from tabula import read_pdf
df = read_pdf('Data/draft-guide2018.pdf',pages='6-7')

# Positional Statistics
statsPageDict = {'QB:Adjusted_Completion_Percentage':'6-7',
                 'QB:Under_Pressure':'8-9',
                 'QB:Deep_Passing':'10-11',
                 'RB:Elusive_Rating':'28-29',
                 'RB:Pass_Blocking_Efficiency':'30-31',
                 'WR:Yards_Per_Route_Run':'49-52',
                 'WR:Deep_Passing':'53-55',
                 'WR:Drop_Rate':'56-59',
                 'WR:Slot_Performance':'60-61',
                 'TE:Yards_Per_Route_Run':'89-90',
                 'OT:Pass_Blocking_Efficiency':'105-107',
                 'OG:Pass_Blocking_Efficiency':'127-128',
                 'OC:Pass_Blocking_Efficiency':'144-145',
                 'CB:Coverage':'158-161',
                 'CB:Slot_Performance':'162-164',
                 'S:Run_Stop_Percentage':'186-188',
                 'S:Tackling_Efficiency':'189-192',
                 'LB:Run_Stop_Percentage':'210-213',
                 'LB:Tackling_Efficiency':'214-217',
                 'LB:Pass_Rush_Opportunity':'218-221',
                 'DT:Pass_Rush_Productivity':'244-248',
                 'DT:Run_Stop_Percentage':'249-253',
                 'DE:Pass_Rush_Productivity':'276-279',
                 'DE:Run_Stop_Percentage':'280-283'}

# Helpful Tutorials
# https://medium.com/dunder-data/selecting-subsets-of-data-in-pandas-6fcd0170be9c
# https://dbsnail.com/2017/11/07/extracting-tables-in-pdf-format-with-tabula-py/
# https://blog.chezo.uno/tabula-py-extract-table-from-pdf-into-python-dataframe-6c7acfa5f302

# Individual Player Statistics
df2 = read_pdf('Data/draft-guide2018.pdf', pages='12')
dfSummary = df2[0:5]