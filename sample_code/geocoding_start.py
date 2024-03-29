# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 09:59:40 2020

@author: fisherd
This file is meant to be an example of a geocoding start to CREDA. Results from
UBID file can readily be combined with results of other files
"""

from CREDA_tools import helper

#Begin run on dataset starting WITH geocodes
project = helper.CREDA_Project("geocodes", "test_data/generic_geo_2.csv", geocoder='generic')

project.assign_shapefile("test_data/san_jose_shapes.csv")
project.perform_piercing()
project.pick_best_match()
project.generate_UBIDs()

project.save_all("UBIDs1.csv")
