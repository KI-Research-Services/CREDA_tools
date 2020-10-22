# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 13:13:49 2020

@author: fisherd
"""

import CREDA_tools.geocoding.arcgis as arcgis
import CREDA_tools.geocoding.census as census
import CREDA_tools.geocoding.generic as generic
import CREDA_tools.geocoding.lightbox as lightbox

class AddressValidator(object):
    '''This is the parent object that all Validators inherit from'''
    def __init__(self, address_df=None):
        self.address_df = address_df

    def get_validator_matches(self):
        '''Generic base method for validator matches'''
        return self.address_df

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
        # TODO add census back in
        # Add GAPI back in
        if validator_type == 'ArcGIS':
            return arcgis.ArcGISValidator(geocode_file)
        if validator_type == 'Lightbox':
            return lightbox.LightBoxValidator(geocode_file)

        # If validator type isn't defined
        return generic.GenericValidator(geocode_file, validator_type)
