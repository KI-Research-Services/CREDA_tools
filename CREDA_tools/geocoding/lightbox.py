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

    def __init__(self, geocode_file: str):
        '''
        This code processes geocoder output from Lightbox

        '''

        super().__init__()
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
            Lightbox_results = pd.read_csv(self.geocode_file)
            Lightbox_results = Lightbox_results[['TempIDZ', 'longitude',
                                                 'latitude', 's_street_number']]
            Lightbox_results.rename(columns={'longitude':'Lightbox_long',
                                             'latitude':'Lightbox_long',
                                             'confidence': 'Lightbox_confidence'},
                                    inplace=True)
            Lightbox_results.set_index('TempIDZ', inplace=True)
            self.address_df = Lightbox_results[['Lightbox_long', 'Lightbox_lat',
                                                'Lightbox_confidence']]
        else:
            print(f'Failed to find file {self.geocode_file}')
