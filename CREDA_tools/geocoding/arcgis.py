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

    score_dict = {'SubAddress':0.95,
                  'PointAddress':0.90,
                  'StreetAddress':0.80,
                  'StreetAddressExt':0.65,
                  'StreetName':0.60,
                  'Locality':0.50
                  }

    def __init__(self, geocode_file):
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
            ArcGIS_results = pd.read_csv(self.geocode_file)
            ArcGIS_results = ArcGIS_results[['USER_TempIDZ', 'Addr_type', 'DisplayX', 'DisplayY']]
            ArcGIS_results['ArcGIS_confidence'] = 0
            for key, value in self.score_dict.items():
                ArcGIS_results.loc[ArcGIS_results['Addr_type'] == key, 'ArcGIS_confidence'] = value
            ArcGIS_results.rename(columns={'DisplayY':'ArcGIS_lat',
                                           'DisplayX':'ArcGIS_long',
                                           'USER_TempIDZ': 'TempIDZ'},
                                  inplace=True)
            ArcGIS_results.set_index('TempIDZ', inplace=True)
            self.address_df = ArcGIS_results[['ArcGIS_long', 'ArcGIS_lat', 'ArcGIS_confidence']]
        else:
            print(f'Failed to find file {self.geocode_file}')
