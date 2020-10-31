# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 15:24:43 2020

@author: fisherd
This file is meant as an example of a basic CREDA_tools run using a Geocoder run from withing the program
Since most geocoders require private access / API keys, we use the free Census geocoder here
"""

from CREDA_tools import helper

# Begin run on dataset 1 by parsing addresses
project = helper.CREDA_Project("addresses", "CREDA_tools/test_data/san_jose_d1.csv")
project.clean_addresses()

# Add a Census geocoding
project.run_geocoding('Census')
project.assign_shapefile("CREDA_tools/test_data/san_jose_shapes.csv")
project.perform_piercing()

# Pick best match sets up the correct shapefile to generate a UBID from
# We are only using a single geocoder, so this step will be fast.
project.pick_best_match()
project.generate_UBIDs()

# Repeat all steps for the second dataset
project2 = helper.CREDA_Project("addresses", "CREDA_tools/test_data/san_jose_d2.csv")
project2.clean_addresses()

project2.run_geocoding('Census')
project2.assign_shapefile("CREDA_tools/test_data/san_jose_shapes.csv")
project2.perform_piercing()
project2.pick_best_match()
project2.generate_UBIDs()

# Produce results, a jaccard joined combination of the two datasets based on UBID
# Saves to outfile.csv
results = project.jaccard_combine(project2, outfile="outfile.csv")

##helper.jaccard_combine(file1, file2)
