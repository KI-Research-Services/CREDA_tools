# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 15:51:06 2021

@author: fisherd
"""

from CREDA_tools import helper

project = helper.CREDA_Project("geocodes", "tstShapesGeocodes.csv", geocoder='generic')

project.assign_shapefile("tstShapes.csv")
#helper.create_shape_pickle("tstShapes.csv", "tstShapes.pickle")
#project.assign_shapefile("tstShapes.pickle")

project.perform_piercing()
project.pick_best_match()
project.generate_UBIDs()

project.save_all("UBIDs1.csv")
