# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 13:13:49 2020

@author: fisherd
"""

class AddressValidator(object):
    '''This is the parent object that all Validators inherit from'''
    def __init__(self, address_df):
        self.address_df = address_df

    def get_validator_matches(self):
        '''Generic base method for validator matches'''
        print("Processing within parent")
        return self.address_df

class ValidatorFactory():
    '''Basic Factory class for validators'''
    def __init__(self):
        pass

    def create_validator(self, validator_type, address_df, geocode_file=None):
        '''Instantiates and returns the requested validator, based on input'''
        if validator_type == 'Census':
            import CREDA_tools.geocoding.census as census
            return census.CensusValidator(address_df, geocode_file) 
        if validator_type == 'ArcGIS':
            import CREDA_tools.geocoding.arcgis as arcgis
            return arcgis.ArcGISValidator(address_df, geocode_file)
        if validator_type == 'GAPI':
            import CREDA_tools.geocoding.gapi as gapi
            return gapi.GAPIValidator(address_df, geocode_file)
        if validator_type == 'Lightbox':
            import CREDA_tools.geocoding.lightbox as lightbox
            return lightbox.LightBoxValidator(address_df, geocode_file)
        return None
