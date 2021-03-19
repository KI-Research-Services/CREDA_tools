# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 23:42:19 2020

@author: fisherd

This file is meant as an example of a basic CREDA_tools run using outside Geocoders.
This employs ArcGIS, a solid industry standard.
"""

from CREDA_tools import helper


# Begin run on dataset 1 through creation of file to Geocode
# NOTE: Below are in windows relative paths. Modify as needed for Linux/Mac or absolute pass
project = helper.CREDA_Project("addresses", "test_data/san_jose_d1.csv")
project.clean_addresses()
project.make_geocoder_file("for_geocoding.csv")

#####Run Geocoding on for_geocoding.csv #####

project.add_geocoder_results('ArcGIS', 'test_data/Arc_output.csv')
project.save_geocoding('test.csv')

#Run rest of steps to UBIDs on dataset 1
project.assign_shapefile("test_data/san_jose_shapes.csv")
project.perform_piercing()
project.generate_UBIDs()

project.save_all("UBIDs1.csv")

#Use a Jaccard join to combine into one dataset
#results = project.jaccard_combine(project2)