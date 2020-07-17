# -*- coding: utf-8 -*-
"""
Created on Mon May 25 22:37:41 2020

@author: fisherd
"""
import os

import pandas as pd

from CREDA_tools.geocoding import validators

class ArcGISValidator(validators.AddressValidator):
    '''This class runs data through the ArcGIS Validator/Geocoder'''
    def __init__(self, address_df):
        super().__init__(address_df)
        self.temp_file = "temp_files\\ArcGIS_temp.csv"
        self.geocode_file = "CREDA_tools\\ceocoding\\geocoding_data\\ArcGIS.csv"
        self.process_addresses()
        
    def process_addresses(self):
        if os.path.exists(self.geocode_file):
            old_run = pd.read_csv(self.geocode_file)
            old_run.drop_duplicates(inplace=True)
            combined = pd.merge(self.address_df, old_run, how ='left', on=['TempIDZ'])

        self.address_df = combined[['TempIDZ','Addr_type','DisplayX','DisplayY']]
        self.address_df.rename(columns = {'Addr_type':'ArcGIS_addr_type', 'DisplayX':'ArcGIS_long',
                                          'DisplayY':'ArcGIS_lat'}, inplace=True)
        
    def run_validator_matches(self, to_process):
        '''Returns validated, Geocoded addresses for self.address_df, using the ArcGIS tool'''
        pass

    def get_validator_matches(self):
        return self.address_df