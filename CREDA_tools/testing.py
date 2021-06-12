# -*- coding: utf-8 -*-
"""
Created on Fri Jun 11 22:40:38 2021

@author: fisherd
"""
from shapely.geometry import Point#, Polygon
from shapely.geos import WKTReadingError #Needed for new error
import shapely.wkt
import buildingid.code as bc

def check_parent_shape(shape1, shape2, overlap_threshold):
    if shape1.area > shape2.area:
        if (shape2.intersection(shape1).area/shape2.area) > overlap_threshold:
            return 'shape1 is parent'
    elif shape2.area > shape1.area:
        if (shape1.intersection(shape2).area/shape1.area) > overlap_threshold:
            return 'shape2 is parent'
    else:
        return 'neither is parent'
    
def check_parent_UBID(UBID1, UBID2, overlap_threshold):
    CodeArea1 = bc.decode(UBID1)
    CodeArea2 = bc.decode(UBID2)
    bbox = CodeArea1.intersection(CodeArea2)
    intersection_area = (bbox[3] - bbox[1]) * (bbox[2] - bbox[0])
    if CodeArea1.area > CodeArea2.area:
        if (intersection_area/CodeArea2.area) > overlap_threshold:
            return 'UBID1 is parent'
    elif CodeArea2.area > CodeArea1.area:
        if (intersection_area/CodeArea1.area) > overlap_threshold:
            return 'UBID2 is parent'
    return 'neither is parent'

def shape_to_UBID(shape, codeLength=16):
    minx, miny, maxx, maxy = shape.bounds
    centerx, centery = (shape.centroid.coords)[0]
    return bc.encode(latitudeLo=miny, longitudeLo=minx, latitudeHi=maxy,
                      longitudeHi=maxx, latitudeCenter=centery,
                      longitudeCenter=centerx, codeLength=codeLength)
