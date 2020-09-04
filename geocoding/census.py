# -*- coding: utf-8 -*-
"""
Created on Mon May 25 21:39:47 2020

@author: fisherd
"""
import os
import time
from pathlib import Path

import censusgeocode as cg
import pandas as pd

from CREDA_tools.geocoding import validators

class CensusValidator(validators.AddressValidator):
    '''This class runs data through the Census Validator/Geocoder'''
    
    score_dict = {'Exact':0.9,
                  'Non_Exact':0.7
                  }
    
    
    def __init__(self, address_df):
        super().__init__(address_df)
        self.temp_file = Path.cwd() / "temp_files" / "Census_temp.csv"
        self.process_addresses()

    def process_addresses(self):
        self.address_df = self.run_validator_matches(self.address_df)
        
    def run_validator_matches(self, to_process):
        '''Returns validated, Geocoded addresses for self.address_df, using the Census tool'''
        to_process = to_process[['single_address', 'city', 'state', 'zip']]
        to_return = pd.DataFrame()
        start = 0
        end = increment = 900
        while end < to_process.shape[0]:
            print(f'Sending from {start} to {end-1}')
            temp = to_process[start:end]
            temp.to_csv(self.temp_file, header=False)
            result = cg.addressbatch(self.temp_file)
            ordered = pd.DataFrame.from_dict(result)
            if to_return.shape[0] == 0:
                to_return = ordered
            else:
                to_return = pd.concat([to_return, ordered])
            start = end
            end = end + increment
            time.sleep(10)
        print(f'Sending from {start} to {end-1}')
        temp = to_process[start:end]
        temp.to_csv(self.temp_file, header=False)
        result = cg.addressbatch(f'temp_files/{self.temp_file.name}')
        ordered = pd.DataFrame.from_dict(result)
        if to_return.shape[0] == 0:
            to_return = ordered
        else:
            to_return = pd.concat([to_return, ordered])

        #All data is now pulled and combined in to_return
        to_return['Census_confidence'] = 0
        for key, value in self.score_dict.items():
            to_return.loc[to_return['matchtype'] == key, 'Census_confidence'] = value
        
        
        to_return = to_return[['id', 'lat', 'lon', 'Census_confidence']]
        to_return.rename(columns={'id':'TempIDZ', 'lat':'Census_lat', 'lon':'Census_long'}, inplace=True)
        to_return.set_index('TempIDZ', inplace=True)
        to_return.index = to_return.index.astype(int)
        #to_return = pd.merge(to_process, to_return, left_index=True, right_index=True)
        return to_return

    def get_validator_matches(self):
        return self.address_df