#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 10:13:51 2018

@author: ejreidelbach

description

:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import os  
import pandas as pd

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================
varNames = ['nameFirst', 'nameLast', 'draftYear', 'college', 'heightFeet', 
            'heightInches','weight', 'wingspan', 'lengthArm', 'lengthHand', 
            'combine10split', 'combine20split', 'combine40dash', 'combineBench', 
            'combineVert', 'combineBroad', 'combineCone', 'combine20shuttle', 
            'combine60shuttle','url','position']
playerDict = {}

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects/NFL')

# Read in JSON file
df = pd.read_json(r'Data/Combine/mockdraftable_data.json')