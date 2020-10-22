# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 09:59:40 2020

@author: fisherd
"""

from CREDA_tools import helper


# Begin run on dataset 1 through creation of file to Geocode
# NOTE: Below are in windows relative paths. Modify as needed for Linux/Mac or absolute pass
project = helper.CREDA_Project("test_data\\san_jose_d1.csv")
project.clean_addresses()
project.make_geocoder_file("for_geocoding.csv")

#Begin run on dataset 2
project2 = helper.CREDA_Project("test_data\\san_jose_d2.csv")
project2.clean_addresses()
project2.make_geocoder_file("for_geocoding2.csv")

#Add Census geocoders
project.run_geocoding('Census')
project2.run_geocoding('Census')

#####Run Geocoding on for_geocoding.csv and for_geocoding2.csv#####

#Add results of ArcGIS geocoding
project.add_geocoder_results('ArcGIS', 'CREDA_tools/test_data/Arc_output.csv')
project2.add_geocoder_results('generic', 'CREDA_tools/test_data/generic_geo_2.csv')

#Run rest of steps to UBIDs on dataset 1
project.assign_shapefile("test_data\\san_jose_shapes.csv")
project.perform_piercing()
project.pick_best_match()
project.generate_UBIDs()

#Run rest of steps to UBIDs on dataset 2
project2.assign_shapefile("test_data\\san_jose_shapes.csv")
project2.perform_piercing()
project2.pick_best_match()
project2.generate_UBIDs()


#Use a Jaccard join to combine into one dataset
results = project.jaccard_combine(project2)
