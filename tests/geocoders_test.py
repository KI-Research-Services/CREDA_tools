# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 08:09:36 2020

@author: fisherd
"""

import os

import pytest

from CREDA_tools.geocoding import validators

def test_canAssertTrue():
    assert True

def test_canCreateObject():
    temp = validators.ValidatorFactory()
    assert type(temp) is validators.ValidatorFactory
    
def test_ArcGisFormat():
    pass

def test_LightboxFormat():
    pass
    
def test_CensusFormat():
    pass
    
def test_censusLiveFormat():
    pass

def test_GapiFormat():
    pass

def test_GapiLiveFormat():
    pass

def test_otherGeocoderFormat():
    pass
