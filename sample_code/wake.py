# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 16:45:12 2021

@author: fisherd
"""

from CREDA_tools import helper

#Begin run on dataset starting WITH geocodes
project = helper.CREDA_Project("geocodes", "../wake_analysis/wake_geocoded_online2.csv", geocoder='ArcGIS')

helper.create_shape_pickle("../wake_analysis/wake_shapes.csv", "wake.pickle")


project.assign_shapefile("wake.pickle")
project.perform_piercing()
project.pick_best_match()
project.generate_UBIDs()

project.save_all("wake_out.csv")