# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 01:51:37 2020

@author: fisherd
"""
import configparser
import os
from pathlib import Path

import pandas as pd

import buildingid.code as bc
from CREDA_tools.address_parsing import algo_grammar
from CREDA_tools.address_parsing import addr_splitter
from CREDA_tools.geocoding import validators
import CREDA_tools.shapes.shapes as SHP


os.chdir("C:\\Users\\fisherd\\Desktop\\projects\\CREDA\\")

def simple_max(row, geocoders):
    found = False
    best_geocoder = ""
    best_geocoder_score = 0
    for geocoder in geocoders:
        if row[f'{geocoder}_status'] == 'Pierced':
            if row[f'{geocoder}_confidence'] > best_geocoder_score:
                best_geocoder = geocoder
                best_geocoder_score = row[f'{geocoder}_confidence']
                found = True
    if found:
        row['best_geocoder'] = best_geocoder
        row['best_geocoder_ShapeID'] = row[f'{best_geocoder}_pierced_ShapeIDs']
        return row
    return None

class CREDA_Project:

    geocoder_results = pd.DataFrame()
    piercing_results = pd.DataFrame()
    best_matches = pd.DataFrame()
    parsed_addresses = pd.DataFrame()
    address_errors = pd.DataFrame()
    shapes = pd.DataFrame()
    UBIDs = pd.DataFrame()

    def __init__(self, filename: str):
        pd.set_option('max_columns', 10)
        infile_path = Path(filename)
        if not infile_path.is_absolute():
            infile_path = Path.cwd() / infile_path
        self.address_file = infile_path

        self.config = configparser.ConfigParser()
        if Path.exists(Path.cwd() / 'config.ini'):
            self.config.read('config.ini')
            print("Using user-provided config.ini file")

        file_lines = pd.read_csv(infile_path)

        # creade TempID
        file_lines.reset_index(inplace=True)
        file_lines.rename(columns={'index':'TempID'}, inplace=True)
        file_lines['TempID'] = file_lines['TempID'] + 1

        address_lines = file_lines[['TempID', 'addr', 'city', 'postal', 'state']].copy()
        self.orig_addresses = address_lines.copy().set_index('TempID')
        self.data_lines = file_lines.drop(columns=['addr', 'city', 'postal',
                                                   'state']).copy().set_index('TempID')
        del file_lines

    def clean_addresses(self):
        address_lines = self.orig_addresses.reset_index()
        address_lines['addr'] = address_lines['addr'].str.lower()
        address_lines['parsed_addr'] = address_lines['addr']
        address_lines['flags'] = None

        for idx, row in address_lines.copy().iterrows():
            temp = algo_grammar.AddrParser(row['addr'], row['postal'], row['city'])
            row['parsed_addr'] = temp.get_addrs()
            row['flags'] = temp.get_flags()
            address_lines.iloc[idx] = row

        temp = addr_splitter.split_df_addresses(address_lines[['TempID', 'parsed_addr']])
        address_lines = pd.merge(address_lines, temp, how='inner', on='TempID')
        self.parsed_addresses = address_lines[['TempID', 'TempIDZ',
                                               'single_address']].set_index('TempIDZ')
        self.address_errors = address_lines[['TempID', 'parsed_addr',
                                             'flags']].set_index('TempID')

    def addr_parse_report(self, outfile: str):
        temp = pd.merge(self.orig_addresses, self.address_errors, how='inner', left_index=True, right_index=True)
        temp.to_csv(outfile)

    def make_geocoder_file(self, outfile: str):
        temp = pd.merge(self.parsed_addresses, self.orig_addresses[['city', 'postal', 'state']], how='inner', left_on='TempID', right_index=True)
        temp.drop(columns='TempID').to_csv(outfile)

    def add_geocoder_results(self, geocoder: str, filename: str):
        pass

    def run_geocoding(self, geocoder: str):
        df_to_geocode = pd.merge(self.parsed_addresses, self.orig_addresses[['city', 'postal', 'state']], how='inner', left_on='TempID', right_index=True)

        validator_factory = validators.ValidatorFactory()
        temp_geocoder = validator_factory.create_validator(geocoder, df_to_geocode)
        validated_df = temp_geocoder.get_validator_matches()

        if self.geocoder_results.shape[0] > 0:
            validated_df = pd.merge(self.geocoder_results, validated_df, how='inner', right_index=True, left_index=True)
        self.geocoder_results = validated_df

    def assign_shapefile(self, shapefile: str):
        # TODO check if already have a shapefile. This will replace current shapefile
        temp_shapefile = Path(shapefile)
        if not temp_shapefile.is_absolute():
            temp_shapefile = Path.cwd() / temp_shapefile
        print(f'Using {temp_shapefile} for parcel piercing')
        self.shapes = SHP.ShapesList(temp_shapefile)

    def perform_piercing(self):
        geocoders = [x[:-4] for x in self.geocoder_results.columns if "_lat" in x]
        for geocoder in geocoders:
            columns = [x for x in self.geocoder_results.columns if geocoder in x]
            temp_pierced = self.shapes.process_df(self.geocoder_results[columns], geocoder, offset=0.0005)
            if self.piercing_results.shape[0] > 0:
                self.piercing_results = pd.merge(self.piercing_results, temp_pierced, how='outer', left_index=True, right_index=True)
            else:
                self.piercing_results = temp_pierced

    def pick_best_match(self, func=None):
        if func is None:
            func = simple_max
        best_match_df = pd.merge(self.geocoder_results, self.piercing_results, how="inner", left_index=True, right_index=True)

        geocoders = [x[:-7] for x in self.piercing_results.columns if "_status" in x]
        best_rows = []

        for _, row in best_match_df.iterrows():
            best_rows.append(func(row, geocoders))
        temp_df = pd.concat(best_rows, axis=1)
        temp_df = temp_df.T
        temp_df['TempIDZ'] = temp_df.index
        temp_df.set_index('TempIDZ', inplace=True)
        self.best_matches = temp_df[['best_geocoder', 'best_geocoder_ShapeID']]

    def generate_UBIDs(self):
        # TODO only handles single match case
        self.best_matches['best_geocoder_ShapeID'] = self.best_matches['best_geocoder_ShapeID'].apply(lambda x: x[0])
        temp = pd.merge(self.best_matches, self.shapes.shape_df[['UBID']], how='left', left_on='best_geocoder_ShapeID', right_index=True)
        self.UBIDs = temp[['UBID']]

    def jaccard_combine(self, other):
        df1_matches = []
        df1_rows = []

        for _, row_1 in self.UBIDs.iterrows():
            ubid_1 = bc.decode(row_1['UBID'])
            for IDZ_2, row_2 in other.UBIDs.iterrows():
                ubid_2 = bc.decode(row_2['UBID'])
                score = ubid_1.jaccard(ubid_2)
                if score:
                    if score > float(self.config['Jaccard']['threshold']):
                        df1_rows.append(row_1)
                        df1_matches.append(IDZ_2)
        results = pd.DataFrame(df1_rows)
        results['MatchIDZ'] = df1_matches
        results.index.rename('TempIDZ', inplace=True)
        results.reset_index()

        results = pd.merge(results, self.data_lines, how='left', left_on='TempIDZ', right_index=True)
        results = pd.merge(results, other.data_lines, how='left', left_on='MatchIDZ', right_index=True)

        return results
