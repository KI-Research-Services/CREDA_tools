# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 01:51:37 2020

@author: fisherd
"""

#Standard Libraries
import configparser
import logging
from pathlib import Path
import pickle

#Third--party Libraries
import buildingid.code as bc
import pandas as pd

from CREDA_tools.address_parsing import algo_grammar
from CREDA_tools.address_parsing import addr_splitter
from CREDA_tools.geocoding import validators
from CREDA_tools.shapes import shapes as SHP

pd.options.mode.chained_assignment = None

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)

#filehandler = logging.FileHandler('CREDA_run.log')
#filehandler.setLevel(logging.DEBUG)

#streamhandler = logging.StreamHandler(logging.INFO)

#logger.addHandler(filehandler)
#logger.addHandler(streamhandler)


def simple_max(row, geocoders):
    found = False
    best_geocoder = ""
    best_geocoder_score = 0
    for geocoder in geocoders:
        if row[f'{geocoder}_status'] in ['Pierced', 'Pierced_Multiple']:
            if row[f'{geocoder}_confidence'] > best_geocoder_score:
                best_geocoder = geocoder
                best_geocoder_score = row[f'{geocoder}_confidence']
                found = True
    if found:
        row['best_geocoder'] = best_geocoder
        row['matching_ShapeIDZ'] = row[f'{best_geocoder}_pierced_ShapeIDZs']
        return row
    return None

def jaccard_combine(file_1, file_2, threshold, outfile):
    df_1 = pd.read_csv(file_1)
    df_2 = pd.read_csv(file_2)

    df_1 = df_1[df_1['UBID'].notna()]
    df_2 = df_2[df_2['UBID'].notna()]

    df1_matches = []
    df1_rows = []

    for _, row_1 in df_1.iterrows():
        ubid_1 = bc.decode(row_1['UBID'])
        for IDZ_2, row_2 in df_2.iterrows():
            ubid_2 = bc.decode(row_2['UBID'])
            score = ubid_1.jaccard(ubid_2)
            if score:
                if score > threshold:
                    df1_rows.append(row_1)
                    df1_matches.append(IDZ_2)
    results = pd.DataFrame(df1_rows)
    results['MatchIDZ'] = df1_matches
    results.index.rename('TempIDZ', inplace=True)

    results = pd.merge(results, df_2, how='left', left_on='MatchIDZ', right_index=True)

    results.to_csv(outfile)

def create_shape_pickle(infile: str, outfile:str) ->None:
    shapefile = SHP.ShapesList(infile)
    pickle.dump(shapefile, open(outfile,"wb"))


class CREDA_Project:

    geocoder_results = pd.DataFrame()
    piercing_results = pd.DataFrame()
    best_matches = pd.DataFrame()
    parsed_addresses = pd.DataFrame()
    TempID_errors = pd.DataFrame()
    TempIDZ_errors = pd.DataFrame()
    shapes = pd.DataFrame()
    UBIDs = pd.DataFrame()
    
    df_list = dict.fromkeys(['TempIDZ','TempID','orig_addresses','parsed_addresses',
                             'geocoder_results','piercing_results','best_matches',
                             'UBIDs','TempID_errors','TempIDZ_errors','data_lines'],
                            pd.DataFrame())

    def __init__(self, entry, filename: str, geocoder='base'):
        #logger.info('\nInitializing run')
        pd.set_option('max_columns', 10)
        infile_path = Path(filename)

        if not infile_path.is_file():
            raise FileNotFoundError('Failed to find infile')

        if not infile_path.is_absolute():
            infile_path = Path.cwd() / infile_path

        self.entry = entry
        self.config = configparser.ConfigParser()
        if Path.exists(Path.cwd() / 'config.ini'):
            self.config.read('config.ini')
            #logger.info("\tUsing user-provided config.ini file")

        if entry == 'addresses':
            self._address_entry(infile_path)
        elif entry == 'geocodes':
            self._geocodes_entry(infile_path, geocoder)
        elif entry == 'parcels':
            self._parcel_entry(infile_path)
        else:
            #logger.info('Valid entry types are "addresses", "geocodes", and "parcels"')
            raise ValueError(f'{entry} not a valid entry type.')

    def _address_entry(self, infile_path):
        #logger.info('\tStarting with addresses')
        file_lines = pd.read_csv(infile_path)
        file_lines.reset_index(inplace=True)
        file_lines.rename(columns={'index':'TempID'}, inplace=True)
        file_lines['TempID'] = file_lines['TempID'] + 1
        for item in ['TempID', 'addr', 'city', 'postal', 'state']:
            if item not in file_lines.columns:
                raise KeyError(f"Your infile doesn't contain the {item} column")
        address_lines = file_lines[['TempID', 'addr', 'city', 'postal', 'state']].copy()
        address_lines = address_lines.fillna('')
        self.orig_addresses = address_lines.copy().set_index('TempID')
        self.data_lines = file_lines.drop(columns=['addr', 'city', 'postal',
                                                   'state']).copy().set_index('TempID')
        self.df_list['orig_addresses'] = self.orig_addresses
        self.df_list['data_lines'] = self.data_lines

    def _geocodes_entry(self, infile_path, geocoder='base'):
        #logger.info('\tStarting with geocodes')
        file_lines = pd.read_csv(infile_path)
        for x in ['lat','long','confidence']:
            if x not in file_lines.columns:
                raise Exception(f'Missing column "{x}" in your geocoder input')
            if file_lines[f'{x}'].dtype == 'object':
                raise Exception(f'You appear to have non-numeric data in column {x}')
        # create TempIDZ
        if 'TempIDZ' not in file_lines.columns:
            file_lines.reset_index(inplace=True)
            file_lines.rename(columns={'index':'TempIDZ'}, inplace=True)
        #logger.debug(file_lines.columns)
        if not 'TempID' in file_lines.columns:
            file_lines['TempID'] = file_lines['TempIDZ']
        self.geocoder_results = file_lines[['TempIDZ','lat','long','confidence']].copy().set_index('TempIDZ')
        self.geocoder_results.columns=[f'{geocoder}_lat',f'{geocoder}_long',f'{geocoder}_confidence']
        self.data_lines = file_lines.drop(columns=['TempIDZ', 'lat', 'long',
                                                   'confidence']).copy().set_index('TempID')
        self.IDs = file_lines[['TempID', 'TempIDZ']].set_index('TempIDZ')
        self.df_list['geocoder_results'] = self.geocoder_results
        self.df_list['data_lines'] = self.data_lines

    def _parcel_entry(self, infile):
        # This will have to accept TempID and geometry
        # It will produce TempIDZ, ShapeID, min/max fields, center fields

        #logger.info('\tStarting with shapes')
        #logger.info(f'\tUsing {infile.name} for parcel piercing')
        if '.pickle' in infile.name:
            self.shapes = pickle.load(open(infile, "rb"))
        else:
            self.shapes = SHP.ShapesList(infile)
        #logger.debug(self.shapes.shape_df.columns)
        self.IDs = self.shapes.shape_df[['ShapeID']].reset_index()
        self.IDs.rename(columns={'ShapeID':'TempID', 'ShapeIDZ':'TempIDZ'}, inplace=True)
        self.best_matches = self.IDs.copy()
        # self.best_matches['matching_ShapeIDZ'] = [[list(self.best_matches['TempIDZ'])]]
        self.best_matches['matching_ShapeIDZ'] = [[x] for x in self.best_matches['TempIDZ']]
        self.IDs.set_index('TempIDZ', inplace=True)
        self.best_matches.set_index('TempIDZ', inplace=True)
        self.df_list['best_matches'] = self.best_matches


    def _UBIDs_entry(self, file_lines):
        # This will have to accept TempID and UBIDs
        # It will produce TempIDZ only. Presumably this will be combined with another
        # project to merge datasets

        # create TempIDZ
        #logger.info('\tStarting with UBIDs')
        file_lines.reset_index(inplace=True)
        file_lines.rename(columns={'index':'TempIDZ'}, inplace=True)
        file_lines['TempIDZ'] = file_lines['TempIDZ'] + 1

        UBID_lines = file_lines[['TempIDZ', 'UBID']].copy()
        if 'TempID' in file_lines.columns:
            UBID_lines['TempID'] = file_lines['TempID']
        else:
            UBID_lines['TempID'] = UBID_lines['TempIDZ']

        self.UBIDs = UBID_lines.copy().set_index('TempIDZ')
        self.data_lines = file_lines.drop(columns=['TempIDZ', 'UBID']).copy().set_index('TempID')
        self.IDs = UBID_lines[['TempID', 'TempIDZ']].set_index('TempIDZ')
        self.df_list['UBIDs'] = self.UBIDs
        self.df_list['data_lines'] = self.data_lines

    def _get_geocoding_errors():
        pass

    def clean_addresses(self):
        #logger.info('\nBeginning Address cleaning step')
        failed_count = 0
        address_lines = self.orig_addresses.reset_index()
        address_lines['addr'] = address_lines['addr'].str.lower()
        address_lines['parsed_addr'] = address_lines['addr']
        address_lines['flags'] = None

        for idx, row in address_lines.copy().iterrows():
            temp = algo_grammar.AddrParser(row['addr'], row['postal'], row['city'])
            row['parsed_addr'] = temp.get_addrs()
            row['flags'] = temp.get_flags()
            failed_count = failed_count + temp.get_status()
            address_lines.iloc[idx] = row

        #logger.debug('Top 5 lines of address df')
        #logger.debug(address_lines.head())
        temp = addr_splitter.split_df_addresses(address_lines[['TempID', 'parsed_addr']])
        address_lines = pd.merge(address_lines, temp, how='inner', on='TempID')
        self.parsed_addresses = address_lines[['TempIDZ',
                                               'single_address']].set_index('TempIDZ')
        self.parsed_addresses = self.parsed_addresses[self.parsed_addresses['single_address'] !=""]
        self.IDs = address_lines[['TempID', 'TempIDZ']].set_index('TempIDZ')
        self.TempID_errors = address_lines[['TempID', 'flags']]
        self.TempID_errors = self.TempID_errors.drop_duplicates(subset='TempID').set_index('TempID')
        self.df_list['parsed_addresses'] = self.parsed_addresses
        self.df_list['TempID_errors'] = self.TempID_errors
        #logger.warn(f'\tFailed to parse {failed_count} addresses')

    def addr_parse_report(self, outfile: str):
        #logger.info(f'\nGenerating parse report at "{outfile}"')
        temp = pd.merge(self.orig_addresses, self.TempID_errors, how='left', left_index=True, right_index=True)
        temp.to_csv(outfile)

    def make_geocoder_file(self, outfile: str):
        #logger.info(f'\nGenerating file to geocode at "{outfile}"')
        temp = pd.merge(self.IDs, self.parsed_addresses, how='inner', left_index=True, right_index = True)
        temp = pd.merge(temp, self.orig_addresses[['city', 'postal', 'state']], how='left', left_on='TempID', right_index=True)
        temp.to_csv(outfile)

    def add_geocoder_results(self, geocoder: str, filename: str):
        #logger.info(f'\nAdding geocoding results from "{filename}"')
        validator_factory = validators.ValidatorFactory()

        temp_geocoder = validator_factory.create_external_validator(geocoder, filename)
        validated_df = temp_geocoder.get_validator_matches()
        if self.geocoder_results.shape[0] > 0:
            validated_df = pd.merge(self.geocoder_results, validated_df, how='outer', right_index=True, left_index=True)
        self.geocoder_results = validated_df
        self.df_list['geocoder_results'] = self.geocoder_results

    def run_geocoding(self, geocoder: str):
        '''
        This function runs a geocoder in real time, provided you have the authentication
        to run it.

        Parameters
        ----------
        geocoder : str
            The specific geocoder you are running. Currently accepts Census. Need to
            add support for GAPI and ArcGIS.

        Returns
        -------
        None.

        '''
        temp = pd.merge(self.parsed_addresses, self.IDs, how='inner', left_index=True, right_index=True)
        df_to_geocode = pd.merge(temp, self.orig_addresses[['city', 'postal', 'state']], how='inner', left_on='TempID', right_index=True)

        validator_factory = validators.ValidatorFactory()
        temp_geocoder = validator_factory.create_realtime_validator(geocoder, df_to_geocode)

        validated_df = temp_geocoder.get_validator_matches()

        if self.geocoder_results.shape[0] > 0:
            validated_df = pd.merge(self.geocoder_results, validated_df, how='inner', right_index=True, left_index=True)
        self.geocoder_results = validated_df
        self.df_list['geocoder_results'] = self.geocoder_results

    def save_geocoding(self, filename: str, data_fields = False, address_fields = False):
        if 'geocoder_results' not in self.df_list.keys():
            #logger.warning('No geocoding to save.')
            return
        field_list = ['geocoder_results']
        if data_fields:
            if not self.df_list['data_fields'].empty:
                field_list.append('data_fields')
            else:
                print('Cannot add data fields as it is not initialized')
        if address_fields:
            if not self.df_list['orig_addresses'].empty:
                field_list.append('orig_addresses')
            else:
                print('Cannot add addresses as they have not initialized')
        self.save_all(filename, field_list)


    def assign_shapefile(self, shapefile: str):
        # TODO check if already have a shapefile. This will replace current shapefile
        temp_shapefile = Path(shapefile)
        if not temp_shapefile.is_absolute():
            temp_shapefile = Path.cwd() / temp_shapefile
        #logger.info(f'\nLoading {temp_shapefile.name} for parcel piercing')
        if '.pickle' in temp_shapefile.name:
            self.shapes = pickle.load(open(temp_shapefile, "rb"))
        else:
            self.shapes = SHP.ShapesList(temp_shapefile)

    def perform_piercing(self):
        #logger.info('\nBeginning parcel piercing')
        geocoders = [x[:-4] for x in self.geocoder_results.columns if "_lat" in x]
        for geocoder in geocoders:
            columns = [x for x in self.geocoder_results.columns if geocoder in x]
            temp_pierced = self.shapes.process_df(self.geocoder_results[columns], geocoder, offset=0.0005)
            if self.piercing_results.shape[0] > 0:
                self.piercing_results = pd.merge(self.piercing_results, temp_pierced, how='outer', left_index=True, right_index=True)
                self.df_list['piercing_results'] = self.piercing_results
            else:
                self.piercing_results = temp_pierced
                self.df_list['piercing_results'] = self.piercing_results
    
    def save_shapes(self, filename):
        self.shapes.shape_df.to_csv(filename)

    def save_piercing(self, filename: str, data_fields = False, address_fields = False):
        if 'piercing_results' not in self.df_list.keys():
            #logger.warning('No piercing yet to save.')
            return
        field_list = ['piercing_results']
        if data_fields:
            if not self.df_list['data_fields'].empty:
                field_list.append('data_fields')
            else:
                print('Cannot add data fields as it is not initialized')
        if address_fields:
            if not self.df_list['orig_addresses'].empty:
                field_list.append('orig_addresses')
            else:
                print('Cannot add addresses as they have not initialized')
        self.save_all(filename, field_list)

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
        self.best_matches = temp_df[['best_geocoder', 'matching_ShapeIDZ']]
        self.df_list['best_matches'] = self.best_matches

    def generate_UBIDs(self):

        if self.best_matches.shape[0] < 1:
            self.pick_best_match()

        UBIDs = [x for y in list(self.best_matches['matching_ShapeIDZ']) for x in y]
        UBIDs = list(set(UBIDs))
        UBIDs = pd.DataFrame(UBIDs, columns=['ShapeIDZ']).set_index('ShapeIDZ')
        #We now have a DataFrame, single column, of unique ShapeIDs

        self.UBIDs = pd.merge(UBIDs, self.shapes.shape_df[['ShapeID','polygon']], how='inner', left_index=True, right_index=True)

        self.UBIDs['UBID'] = self.UBIDs['polygon'].apply(SHP.get_UBID)
        self.UBIDs.drop(columns=['polygon'], inplace=True)
        #self.df_list['UBIDs'] = self.UBIDs

    def save_UBIDs(self, filename: str, data_fields = False, address_fields = False):
        if 'geocoder_results' not in self.df_list.keys():
            #logger.warning('No UBIDs to save.')
            return
        field_list = ['UBIDs']
        if data_fields:
            if not self.df_list['data_fields'].empty:
                field_list.append('data_fields')
            else:
                print('Cannot add data fields as it is not initialized')
        if address_fields:
            if not self.df_list['orig_addresses'].empty:
                field_list.append('orig_addresses')
            else:
                print('Cannot add addresses as they have not initialized')
        self.save_all(filename, field_list)

    def save_all(self, outfile, field_list=None):
        #logger.info(f'\nSaving data to {outfile}')
        temp = self.IDs
        #logger.debug(f'Start of ID lines:\n{temp.head()}')
        if not field_list:
            field_list = self.df_list.keys()
        for key in field_list:
            df = self.df_list[key]
            if not df.empty:
                if df.index.name == 'TempIDZ':
                    temp = pd.merge(temp, df, how='left', left_index=True, right_index=True)
                if df.index.name == 'TempID':
                    temp = pd.merge(temp, df, how='left', left_on='TempID', right_index=True)
        #logger.debug(f'columns in temp object after merging:\n{temp.columns}')
        if self.UBIDs.shape[0]>0:
            final_rows = []
            temp = temp.reset_index()
            print(temp.columns)
            for _, row in temp[temp['matching_ShapeIDZ'].notna()].iterrows():
                for item in row['matching_ShapeIDZ']:
                    row['single_ShapeIDZ'] = item
                    final_rows.append(row.copy())
            for _, row in temp[~temp['matching_ShapeIDZ'].notna()].iterrows():
                final_rows.append(row.copy())
            final_df = (pd.DataFrame(final_rows))

            #Merge with shape_df to get associate shapes
            final_df = pd.merge(final_df, self.UBIDs['ShapeID'], how = 'left', left_on='single_ShapeIDZ', right_index=True)
            final_df = pd.merge(final_df, self.UBIDs.reset_index(), how = 'left', left_on='ShapeID', right_on='ShapeID')

        else:
            final_df = temp
        final_df.to_csv(outfile)

'''
    def jaccard_combine(self, other, outfile=None):
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

        results = pd.merge(results, self.parsed_addresses[['single_address']], how='left', left_on='TempIDZ', right_index=True)
        results = pd.merge(results, other.parsed_addresses[['single_address']], how='left', left_on='MatchIDZ', right_index=True)

        if outfile:
            results.to_csv(outfile)
        return results
'''

'''
buildingid crossref UBIDs1.csv UBIDs2.csv jaccard.csv --left-fieldname-code="UBID" --right-fieldname-code="UBID"

infile1 = 'UBIDs1.csv'
infile2 = 'UBIDs2.csv'
outfile = 'jaccard.csv'

os.system(f'buildingid crossref {infile1} {infile2} {outfile} --left-fieldname-code="UBID" --right-fieldname-code="UBID"')
'''