# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 12:16:30 2020

@author: fisherd
"""

import os
from pathlib import Path

import pandas as pd

# my libraries
from CREDA_tools.address_parsing import algo_grammar
from CREDA_tools.address_parsing import addr_splitter
from CREDA_tools.geocoding import validators
import CREDA_tools.shapes.shapes as SHP
import buildingid.code as bc

class CREDA_Project():
    '''This class acts as an easy pipeline tool to simplify CREDA analyses'''
    supported_analyses = ['ArcGIS', 'Lightbox', 'GAPI', 'Census']

    def __init__(self, name: str):
        '''
        Basic initialization for the analysis helper. First, creates the folder
        structure for the new analysis. Second, sets up the needed variables.
        Finally, it prints the current run status via the print_run() function.

        Parameters
        ----------
        name : str
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        run_dir = Path.cwd() / name

        if not os.path.exists(run_dir):
            os.mkdir(run_dir)
        for folder in ['addresses_in', 'addresses_out', 'logs', 'final_results',
                       'geocoded_in', 'piercing_results', 'shapefiles', 'temp_files']:
            os.makedirs(run_dir / folder, exist_ok=True)

        print(f'Run {name} created.')

        os.chdir(run_dir)
        print(f'Changing working directory to {run_dir}')

        # setting up variables needed for rest of the run
        self.run_name = name
        self.sources = {}
        self.source_analyses = {}
        self.parsed_addresses = []
        self.address_index = {}

        self.print_run()

    def print_run(self):
        '''
        This is a description of the current run setup. It includes the different
        sources files we have, the geocoders being used on each, etc.

        Returns
        -------
        None.

        '''
        print(f'\n***{self.run_name}***')
        print('----------------------------------------------')
        if self.sources:
            for source, analyses in self.source_analyses.items():
                infile = self.sources[source]
                print(f"Source {source} - {infile}")
                if len(analyses) > 0:
                    for analysis in analyses:
                        print(f'\t{analysis}', end="")
                        if analysis in self.supported_analyses:
                            print(" - supported")
                        else:
                            print(" - custom")
                else:
                    print(f'\tNo analyses added yet for {source}')
                print('\n')
        else:
            print('No sources added yet')


    def add_data_source(self, source_name: str, source_file: str):
        '''
        This allows you to add an address file to the analysis.

        Parameters
        ----------
        source_name : str
            What you want to call the source
        source_file : str
            The filename of the source

        Returns
        -------
        None.

        '''
        temp_path = Path(source_file)
        if not temp_path.is_absolute():
            temp_path = Path.cwd() / "addresses_in" / temp_path
        self.sources[source_name] = temp_path
        self.source_analyses[source_name] = []

        self.print_run()


    def add_geocoder(self, source_name: str, geocoder: str):
        '''
        This allows you to add a geocoder to the analysis. Currently, this will
        not run a geocoder but can access geocoded addresses in the
        "geocoder_in" folder

        Parameters
        ----------
        source_name : str
            The name of your source. Must match a source already added
        geocoder : str
            The name of the geocoder

        Returns
        -------
        None.

        '''

        if source_name in self.sources.keys():
            self.source_analyses[source_name].append(geocoder)
        else:
            print("Invalid source name. Make sure have added with the add_data_source function")
        self.print_run()


    def remove_geocoder(self, source_name: str, geocoder: str):
        '''
        This allows you to remove a geocoder from the analysis.

        Parameters
        ----------
        source_name : str
            DESCRIPTION.
        geocoder : str
            DESCRIPTION.

        Returns
        -------
        None.

        '''

        if source_name in self.sources.keys():
            if geocoder in self.source_analyses[source_name]:
                self.source_analyses[source_name].remove(geocoder)
        else:
            print("Invalid source/analysis combination")
        self.print_run()

    def run_addresses(self):
        '''
        This function runs all address files through the address parser and
        splitter functions. The address output is retained in memory, and
        intermediate output files are stored in the address_out directory

        Returns
        -------
        None.

        '''
        for source, address_file in self.sources.items():
            address_lines = pd.read_csv(address_file)
            address_lines.reset_index(inplace=True)
            address_lines.rename(columns={'index':'TempID'}, inplace=True)
            address_lines['TempID'] = address_lines['TempID'] + 1

            try:
                address_lines['addr'] = address_lines['addr'].str.lower()
            except KeyError:
                print("\n***ERROR***\n-Invalid input format. Infile must have"
                      " address columns 'addr'.")
                print(address_lines.columns)
                return None
            address_lines['parsed_addr'] = address_lines['addr']
            address_lines['flags'] = ""

            # TODO can I speed this up with an apply returning a list???
            for idx, row in address_lines.copy().iterrows():
                temp = algo_grammar.AddrParser(row['addr'])
                row['parsed_addr'] = temp.get_addrs()
                row['flags'] = temp.get_flags()
                address_lines.iloc[idx] = row

            temp = addr_splitter.split_df_addresses(address_lines[['TempID', 'parsed_addr']])
            address_lines = pd.merge(address_lines, temp, how='inner', on='TempID')
            #outfile = f'{self.run_name}\\addresses_out\\{source}.csv'
            outfile = Path.cwd() / 'addresses_out' / f'{source}.csv'
            address_lines = address_lines[['TempID', 'TempIDZ', 'addr',
                                           'single_address', 'city', 'state',
                                           'zip', 'parsed_addr', 'flags']]
            address_lines.set_index('TempIDZ', inplace=True)
            address_lines.to_csv(outfile, index=False)
            self.parsed_addresses.append(address_lines)
            self.address_index[source] = len(self.parsed_addresses) - 1
        return None


    def add_geocoder_results(self):
        '''
        This function goes through each geocoder for each set of parsed addresses,
        so by the end of this function each address set should have at least 3
        addtional columns per geocoder, 1 each for latitude and longitude, and one
        for a measure of confidence.

        Returns
        -------
        None.

        '''

        validator_factory = validators.ValidatorFactory()

        for source, geocoders in self.source_analyses.items():

            geocoded_addrs = self.parsed_addresses[self.address_index[source]]

            for geocoder in geocoders:

                geocode_file = Path.cwd() / "geocoded_in" / f'{source}_{geocoder}.csv'
                temp_validator = validator_factory.create_validator(
                    geocoder, geocoded_addrs, geocode_file)
                validated_df = temp_validator.get_validator_matches()
                geocoded_addrs = pd.merge(geocoded_addrs, validated_df,
                                          left_index=True, right_index=True, how='left')
                print(f'Added on {geocoder} geocoding to source {source}')

            self.parsed_addresses[self.address_index[source]] = geocoded_addrs

    def perform_piercing(self, shapefile: str):
        '''
        This function loads the shapefile and runs each set up geocoder coords
        against it to check piercing.

        Parameters
        ----------
        shapefile : str
            CSV wkt shapefile, preferably in the shapefiles folder.

        Returns
        -------
        None.

        '''
        temp_shapefile = Path(shapefile)
        if not temp_shapefile.is_absolute():
            temp_shapefile = Path.cwd() / "shapefiles" / temp_shapefile
        print(temp_shapefile)
        self.shapes = SHP.ShapesList(temp_shapefile)
        for source, geocoders in self.source_analyses.items():
            geocoded_addrs = self.parsed_addresses[self.address_index[source]]

            for geocoder in geocoders:
                temp_pierced = self.shapes.process_df(geocoded_addrs, geocoder, offset=0.0005)
                geocoded_addrs = pd.merge(geocoded_addrs, temp_pierced, how='left',
                                          left_index=True, right_index=True)
            #geocoded_addrs.to_csv(f'{self.run_name}\\piercing_results\\{source}.csv')
            geocoded_addrs.to_csv(Path.cwd() / 'piercing_results' / f'{source}.csv')
            self.parsed_addresses[self.address_index[source]] = geocoded_addrs

    def select_best_match(self):
        '''
        For each address this selects the best match based on pure confidence
        scores. It saves the new dataframe to the project object and a copy to
        the final_results folder

        Returns
        -------
        None.

        '''
        for source, geocoders in self.source_analyses.items():
            #print(f'geocoders are {geocoders}')
            addresses_with_pierced = self.parsed_addresses[self.address_index[source]]
            best_rows = []
            for row in addresses_with_pierced.iterrows():
                #print(row)
                found = False
                best_geocoder = ""
                best_geocoder_score = 0
                for geocoder in geocoders:
                    if row[f'{geocoder}_status'] == 'Pierced':
                        if row[f'{geocoder}_confidence'] > best_geocoder_score:
                            best_geocoder = geocoder
                            best_geocoder_score = row[f'{geocoder}_confidence']
                            found = True
                        else:
                            pass
                            #print(row[f'{geocoder}_confidence'], end=" ")
                            #print(f'vs {best_geocoder_score}')
                    else:
                        pass
                        #print(row[f'{geocoder}_status'])

                if found:
                    row['best_geocoder'] = best_geocoder
                    row['best_geocoder_id'] = row[f'{best_geocoder}_pierced_ids']
                    best_rows.append(row)
            temp_df = pd.concat(best_rows, axis=1)
            temp_df = temp_df.T

            temp_df = self.add_shapes(temp_df)

            temp_df.to_csv(Path.cwd() / 'final_results' / f'{source}_results.csv')
            self.parsed_addresses[self.address_index[source]] = temp_df

    def add_shapes(self, temp_df):
        '''
        Takes completed output from the piercing and adds back in WKT on the best
        matching shapeID

        Parameters
        ----------
        temp_df : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''

        # TODO fix for multiple pierced shapes case
        temp_df['best_geocoder_id'] = temp_df['best_geocoder_id'].map(lambda x: x[0])
        temp_df = pd.merge(temp_df, self.shapes.shape_df,
                           left_on='best_geocoder_id', right_on='shapeID')
        return temp_df

    def ConvertToUBIDs(self):
        '''
        This function goes through each source and geocoder and converts the current
        Geometry from WKT to UBIDs

        Returns
        -------
        None.

        '''
        #for source, geocoders in self.source_analyses.items():
        for source in self.source_analyses.keys():

            temp_dict = {}
            df = self.parsed_addresses[self.address_index[source]]
            for idx, row in df.iterrows():
                UBID = bc.encode(latitudeLo=row['miny'],
                                 longitudeLo=row['minx'],
                                 latitudeHi=row['maxy'],
                                 longitudeHi=row['maxx'],
                                 latitudeCenter=row['centery'],
                                 longitudeCenter=row['centerx'],
                                 codeLength=16)
                temp_dict[idx] = UBID

            UBID_df = pd.DataFrame.from_dict(temp_dict, orient='index')
            UBID_df.columns = ['UBID']

            self.parsed_addresses[self.address_index[source]] = pd.merge(df, UBID_df, how='left', left_index=True, right_index=True)
