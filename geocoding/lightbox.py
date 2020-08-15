# -*- coding: utf-8 -*-
"""
Created on Tue May 26 13:15:29 2020

@author: fisherd
"""

import os

import pandas as pd

from CREDA_tools.geocoding import validators

class LightBoxValidator(validators.AddressValidator):
    '''This class runs data through the LightBox Validator/Geocoder'''
    
    def __init__(self, address_df: pd.DataFrame, geocode_file: str):
        '''
        The init for the LightBoxValidator class takes the actual geocoded file
        and adds it to the current dataframe of address. After processing, the
        new dataframe can be retrieved from get_validator_matches()

        Parameters
        ----------
        address_df : pd.DataFrame
            DESCRIPTION.
        geocode_file : str
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        
        super().__init__(address_df)
        self.temp_file = self.run_dir / "temp_files" / "LightBox_temp.csv"
        self.geocode_file = geocode_file
        self.process_addresses()
        
    def process_addresses(self):
        if os.path.exists(self.geocode_file):
            old_run = pd.read_csv(self.geocode_file)
            old_run.drop_duplicates(inplace=True)
            combined = pd.merge(self.address_df, old_run, how ='left', on=['TempIDZ'])

        self.address_df = combined[['TempIDZ','longitude','latitude', 's_street_number']]
        self.address_df.rename(columns = {'longitude':'Lightbox_long',
                                          'latitude':'Lightbox_lat',
                                          's_street_number':'Lightbox_confidence'}, inplace=True)
        
    def run_validator_matches(self, to_process):
        '''Returns validated, Geocoded addresses for self.address_df, using the LightBox tool'''
        pass

    def get_validator_matches(self):
        return self.address_df