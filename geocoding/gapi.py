# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 01:03:55 2020

@author: fisherd
"""

import os

import pandas as pd

from CREDA_tools.geocodingeocoding import validators

class GAPIValidator(validators.AddressValidator):
    '''This class runs data through the GAPI Validator/Geocoder'''
    def __init__(self, address_df):
        super().__init__(address_df)
        self.temp_file = "temp_files\\GAPI_temp.csv"
        self.geocode_file = "CREDA_tools\\geocoding\\geocoding_data\\GAPI.csv"
        self.process_addresses()
        
    def process_addresses(self):
        if os.path.exists(self.geocode_file):
            old_run = pd.read_csv(self.geocode_file)
            old_run.drop_duplicates(inplace=True)
            combined = pd.merge(self.address_df, old_run, how ='left', on=['TempIDZ'])

        self.address_df = combined[['TempIDZ','longitude','latitude']]
        self.address_df.rename(columns = {'addr_type':'GAPI_addr_type','lat':'GAPI_lat','long':'GAPI_long','loc_type':'GAPI_loc_type'}, inplace=True)
        
    def run_validator_matches(self, to_process):
        '''Returns validated, Geocoded addresses for self.address_df, using the LightBox tool'''
        pass

    def get_validator_matches(self):
        return self.address_df