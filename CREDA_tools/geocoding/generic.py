# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 00:05:18 2020

@author: fisherd
"""

import os

import pandas as pd

from CREDA_tools.geocoding import validators

class GenericValidator(validators.AddressValidator):
    '''This class opens output from a generic geocoder and adds it to the output'''

    def __init__(self, geocode_file, validator_type):
        super().__init__()
        self.validator_type = validator_type
        self.geocode_file = geocode_file
        self.add_data()

    def add_data(self):
        '''
        This is the standard geocoder function to add the file data as geocoder results

        Returns
        -------
        None.

        '''
        print('Using generic geocoder')
        if os.path.exists(self.geocode_file):
            geocode_results = pd.read_csv(self.geocode_file)
            if 'TempIDZ' not in geocode_results.columns:
                geocode_results.reset_index(inplace=True)
                geocode_results.rename(columns={'index':'TempIDZ'}, inplace=True)
            
            geocode_results.set_index('TempIDZ', inplace=True)
            cols_to_move = ['lat', 'long', 'confidence']
            geocode_results = geocode_results[cols_to_move + [col for col in geocode_results.columns if col not in cols_to_move]]
            geocode_results.columns = [f'{self.validator_type}_{col}' for col in geocode_results.columns]
            
            self.address_df = geocode_results
            
        else:
            print(f'Failed to find file {self.geocode_file}')
