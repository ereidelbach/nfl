#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 24 12:54:49 2018

@author: ejreidelbach

:DESCRIPTION:
    - This script will read in scraped JSONs from NFL.com and flatten the nested
        portions of those JSON files (the career and situational stats) which
        are currently stored in lists. This script will unpack those nested 
        lists and flatten them such that every variable is placed in its own
        column whereas every player will be in his own row.

:REQUIRES:
   
:TODO:
"""
 
#==============================================================================
# Package Import
#==============================================================================
import json
import pandas as pd
import os

#==============================================================================
# Function Definitions / Reference Variable Declaration
#==============================================================================

#==============================================================================
# Working Code
#==============================================================================

# Set the project working directory
os.chdir(r'/home/ejreidelbach/projects')
