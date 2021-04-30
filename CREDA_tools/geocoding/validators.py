# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 13:13:49 2020

@author: fisherd
"""

class AddressValidator(): # pylint: disable=too-few-public-methods
    '''This is the parent object that all Validators inherit from'''
    def __init__(self, address_df=None):
        self.address_df = address_df

    def get_validator_matches(self):
        '''Generic base method for validator matches'''
        return self.address_df

import CREDA_tools.geocoding.census as census
import CREDA_tools.geocoding.generic as generic

class ValidatorFactory():
    '''Basic Factory class for validators'''
    def __init__(self):
        pass

    @staticmethod
    def create_realtime_validator(validator_type, address_df):
        '''Instantiates and returns the requested validator, based on input'''
        if validator_type == 'Census':
            return census.CensusValidator(address_df)
        # TODO Add GAPI back in
        return None

    @staticmethod
    def create_external_validator(validator_type, geocode_file):
        '''Instantiates and returns the requested validator, based on input'''
        # Clean up post removing ArcGIS, GAPI, and Lightbox
        return generic.GenericValidator(geocode_file, validator_type)
