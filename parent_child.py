# -*- coding: utf-8 -*-
"""
Created on Thu Jun  3 16:52:27 2021

@author: fisherd
"""

from shapely.geometry import Point#, Polygon
from shapely.geos import WKTReadingError #Needed for new error
import shapely.wkt
import buildingid.code as bc

from CREDA_tools import testing

WKT_1 = "POLYGON((-78.62782859776053 35.73570013770042,-78.62557983398436 35.73560259888056,-78.625150680542 35.738486907349795,-78.62781143188477 35.73883524673148,-78.62923622052767 35.738110699265334,-78.62782859776053 35.73570013770042))"
WKT_2 = "POLYGON((-78.62782859776053 35.73570013770042,-78.62557983398436 35.73560259888056,-78.62781143188477 35.73883524673148,-78.62923622052767 35.738110699265334,-78.62782859776053 35.73570013770042))"

shape1 = shapely.wkt.loads(WKT_1)
shape2 = shapely.wkt.loads(WKT_2)

UBID1 = testing.shape_to_UBID(shape1)
UBID2 = testing.shape_to_UBID(shape2)

print(testing.check_parent_shape(shape1, shape2, 0.7))
print(testing.check_parent_UBID(UBID1, UBID2, 0.7))
