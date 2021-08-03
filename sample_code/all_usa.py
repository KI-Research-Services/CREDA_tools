# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 16:33:05 2021

@author: fisherd
"""

import nation_parse as np
from CREDA_tools import helper

#Begin run on nationwide dataset starting WITH geocodes
np.process_nationwide_from_geocodes("test_data/generic_geo_2.csv",
                                    shelf_file = 'D:/shape_shelf/shapes',
                                    outfile='temp/whatever_I_want.csv')
