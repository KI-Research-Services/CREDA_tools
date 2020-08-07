# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 12:16:30 2020

@author: fisherd
"""

import pandas as pd

# my libraries
from CREDA_tools.address_parsing import algo_grammar
from CREDA_tools.address_parsing import addr_splitter
from CREDA_tools.geocoding import validators
import CREDA_tools.shapes.shapes as SHP

class CREDA_Project():
    '''This class acts as an easy pipeline tool to simplify CREDA analyses'''
    supported_analyses = ['ArcGIS', 'Lightbox', 'GAPI']

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

        '''
        os.mkdir(name)
        for folder in ['address_in', 'address_out', 'logs', 'geocode_in', 'shapes']:
            os.mkdir(f'{name}\\{folder}')
        '''
        print(f'Run {name} created.')

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
        print('-Add a source with function add_data_source(source_name, file)')
        print('-Add a geocoder to a source with function add_geocoder(source_name, geocoder)')
        print('Possible geocoders include "ArcGIS", "Lightbox", "GAPI", etc.')
        print('Or give it a different name and it will look for that file')

        print("\n***Start run with the address_parse function***")


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
        self.sources[source_name] = source_file
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
            address_file = f'{self.run_name}\\addresses_in\\{address_file}'
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

            for idx, row in address_lines.copy().iterrows():
                temp = algo_grammar.AddrParser(row['addr'])
                row['parsed_addr'] = temp.get_addrs()
                row['flags'] = temp.get_flags()
                address_lines.iloc[idx] = row

            temp = addr_splitter.split_df_addresses(address_lines[['TempID', 'parsed_addr']])
            address_lines = pd.merge(address_lines, temp, how='inner', on='TempID')
            outfile = f'{self.run_name}\\addresses_out\\{source}.csv'
            address_lines = address_lines[['TempID', 'TempIDZ', 'addr', 'single_address', 'city', 'state', 'zip', 'parsed_addr', 'flags']]
            address_lines[['TempID', 'TempIDZ', 'addr', 'single_address', 'city', 'state', 'zip']].to_csv(outfile, index=False)
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
                geocode_file = f'{self.run_name}\\geocoded_in\\{source}_{geocoder}.csv'
                print(f'Expecting infile at {geocode_file}')
                temp_validator = validator_factory.create_validator(geocoder, geocoded_addrs, geocode_file)
                validated_df = temp_validator.get_validator_matches()
                geocoded_addrs = pd.merge(geocoded_addrs, validated_df, on='TempIDZ', how='left')
                print(f'Added on {geocoder} geocoding to source {source}')
            self.parsed_addresses[self.address_index[source]] = geocoded_addrs
            print(geocoded_addrs.columns)

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
        shapes = SHP.ShapesList(shapefile)

        for source, geocoders in self.source_analyses.items():
            geocoded_addrs = self.parsed_addresses[self.address_index[source]]

            for geocoder in geocoders:
                temp_pierced = shapes.process_df(geocoded_addrs, geocoder, offset=0.0005)
                geocoded_addrs = pd.merge(geocoded_addrs, temp_pierced, how='left', on='TempIDZ')
            geocoded_addrs.to_csv(f'{self.run_name}\\piercing_results\\{source}.csv')
            self.parsed_addresses[self.address_index[source]] = geocoded_addrs

    def select_best_match(self):
        for source, geocoders in self.source_analyses.items():
            #print(f'geocoders are {geocoders}')
            addresses_with_pierced = self.parsed_addresses[self.address_index[source]]
            best_rows = []
            for idx, row in addresses_with_pierced.iterrows():
                #print(row)
                found = False
                best_geocoder = ""
                best_geocoder_score = 0
                for geocoder in geocoders:
                    #print(f'geocoder is {geocoder}')
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
                    row['best_geocoder_APN'] = row[f'{best_geocoder}_Pierced_APNs']
                    best_rows.append(row)
            temp_df = pd.concat(best_rows)
            print('Reached the end')
            print(best_rows)
            print(temp_df)
                
                