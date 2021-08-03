# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 13:46:12 2021

@author: fisherd
"""

from CREDA_tools import helper
import shelve
import pandas as pd
import math
from collections import defaultdict

def process_nationwide_from_geocodes(infile, outfile='temp/combined_out.csv', shelf_file = 'D:/shape_shelf/shapes'):
    shape_shelf = shelve.open(shelf_file)

    # Recover geocoding, split into boxes
    project = helper.CREDA_Project("geocodes", infile, geocoder='generic')
    
    geo_results = project.geocoder_results.reset_index()
    
    boxes = defaultdict(list)
    outfiles = []
    
    #Assign boxes
    for idx, row in geo_results.iterrows():
        x = math.floor(row['generic_long'])
        y = math.floor(row['generic_lat'])
        x = str(x) if x>0 else 'n'+str(x)[1:]
        y = str(y) if y>0 else 'n'+str(y)[1:]
        boxes[f'box_{x}_{y}'].append(row)
    
    for box in boxes.keys():
        temp = pd.DataFrame(boxes[box])
        temp.columns = ['TempIDZ', 'lat', 'long', 'confidence']
        temp.to_csv('temp/temp_geo.csv')
        temp_project = helper.CREDA_Project("geocodes", "temp/temp_geo.csv", geocoder='generic')
        temp_project.shapes = shape_shelf[box]
        temp_project.perform_piercing()
        temp_project.pick_best_match()
        temp_project.generate_UBIDs()
        
        temp_outfile = f'temp/{box}.csv'
        temp_project.save_all(temp_outfile)
        outfiles.append(temp_outfile)
    
    combined_csv = pd.concat([pd.read_csv(f) for f in outfiles ])
    combined_csv.to_csv(outfile, index=False)
    print(f'Analysis finished and saved to {outfile}')