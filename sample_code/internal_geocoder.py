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