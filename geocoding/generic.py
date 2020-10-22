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
        if os.path.exists(self.geocode_file):
            geocode_results = pd.read_csv(self.geocode_file)
            print(geocode_results)
            geocode_results = geocode_results[['TempIDZ', 'lat', 'long', 'confidence']]
            geocode_results.rename(columns={'lat':f'{self.validator_type}_lat',
                                            'long':f'{self.validator_type}_long',
                                            'confidence': f'{self.validator_type}_confidence'},
                                   inplace=True)
            geocode_results.set_index('TempIDZ', inplace=True)
            self.address_df = geocode_results[[f'{self.validator_type}_lat',
                                               f'{self.validator_type}_long',
                                               f'{self.validator_type}_confidence']]
        else:
            print(f'Failed to find file {self.geocode_file}')
