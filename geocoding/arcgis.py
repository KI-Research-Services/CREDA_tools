# -*- coding: utf-8 -*-
"""
Created on Mon May 25 22:37:41 2020

@author: fisherd
"""

import os
from pathlib import Path

import pandas as pd

from CREDA_tools.geocoding import validators

class ArcGISValidator(validators.AddressValidator):
    '''This class runs data through the ArcGIS Validator/Geocoder'''
    
    score_dict = {'SubAddress':0.95,
                  'PointAddress':0.90,
                  'StreetAddress':0.80,
                  'StreetAddressExt':0.65,
                  'StreetName':0.60,
                  'Locality':0.50
                  }
    
    def __init__(self, address_df, geocode_file):
        super().__init__(address_df)
        self.temp_file = Path.cwd() / "temp_files" / "ArcGIS_temp.csv"
        self.geocode_file = geocode_file
        self.process_addresses()
        
    def process_addresses(self):
        if os.path.exists(self.geocode_file):
            print("Path exists")
            old_run = pd.read_csv(self.geocode_file)
            old_run.drop_duplicates(inplace=True)
            print(f'{type(self.address_df)} {type(old_run)}')
            combined = pd.merge(self.address_df, old_run, how ='left', on=['TempIDZ'])
        else:
            print(f'Failed to find file {self.geocode_file}')
        
        combined['ArcGIS_confidence'] = 0
        for key, value in self.score_dict.items():
            combined.loc[combined['Addr_type'] == key, 'ArcGIS_confidence'] = value
        self.address_df = combined[['TempIDZ','ArcGIS_confidence','DisplayX','DisplayY']]
        self.address_df.rename(columns = {'DisplayX':'ArcGIS_long',
                                          'DisplayY':'ArcGIS_lat'}, inplace=True)
        
    def run_validator_matches(self, to_process):
        '''Returns validated, Geocoded addresses for self.address_df, using the ArcGIS tool'''
        pass

    def get_validator_matches(self):
        return self.address_df