# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 10:38:46 2020

@author: fisherd
"""

import pandas as pd

from CREDA_tools.geocoding import validators

class Geocoder():
    
    def __init__(self):
        self.validator_factory = validators.ValidatorFactory()

    def add_geocoding(self, addr_df, validator, geocode_file=None):
        temp_validator = self.validator_factory.create_validator(validator, addr_df, geocode_file)
        validated_df = temp_validator.get_validator_matches()
        geocoded = pd.merge(addr_df, validated_df, on='TempIDZ', how='left')
        print(f'Added on geocoding for {validator}')
        return geocoded