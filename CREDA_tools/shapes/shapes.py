# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 10:10:38 2020

@author: fisherd
"""

import pandas as pd
from shapely.geometry import Point#, Polygon
from shapely.geos import WKTReadingError #Needed for new error
import shapely.wkt

import buildingid.code as bc

def unpack(WKT_object):
    if WKT_object.geom_type != 'Polygon':
        return_list = []
        WKT_list = list(WKT_object)
        for WKT in WKT_list:
            return_list.extend(unpack(WKT))
        return return_list
    else:
        return [WKT_object]
        

class ShapesList():
    
    def __init__(self, file):
        shape_frame = pd.read_csv(file)
        shape_frame.dropna(inplace=True)
        shape_frame.drop_duplicates(inplace=True)
        shapes = []
        self.failed_shapes = []
        shapeIDZ = 0
        #For each shape, change to polygon, and get min/max coords. Append to list of dictionaries
        for idx, item in shape_frame.iterrows():
            if 'ShapeID' in shape_frame.columns:
                index = item.PARCEL_APN
            else:
                index = idx
            try:
                WKT = shapely.wkt.loads(item.GEOM)
                WKT_shapes = unpack(WKT)
                #print(len(WKT_shapes))
                for polygon in WKT_shapes:
                    minx, miny, maxx, maxy = polygon.bounds
                    centerx, centery = (polygon.centroid.coords)[0]
                    UBID = bc.encode(latitudeLo=miny,
                                     longitudeLo=minx,
                                     latitudeHi=maxy,
                                     longitudeHi=maxx,
                                     latitudeCenter=centery,
                                     longitudeCenter=centerx,
                                     codeLength=16)
                    shapes.append({'shapeID':index, 'shapeIDZ':shapeIDZ, 'polygon':polygon.to_wkt(),
                                   'minx':minx, 'maxx':maxx, 'miny': miny, 'maxy':maxy,
                                   'centerx':centerx, 'centery':centery, 'UBID': UBID})
                    shapeIDZ = shapeIDZ + 1
            except WKTReadingError:
                self.failed_shapes.append(idx)
        
        #Create dataframe for shapes, this time with min/max
        #We can probably do this with a .apply() method, but the above loop was clear enough.
        self.shape_df = pd.DataFrame.from_dict(shapes)
        self.shape_df.set_index('shapeIDZ', inplace=True)
        
    def process_df(self,complete_df:pd.DataFrame, validator:str, offset:float = 0):
        print(f'\tProcessing for {validator}')
        results = []
        subset_df = complete_df[[f'{validator}_long',f'{validator}_lat']]
        subset_df.columns = ['long','lat']
        count = 0
        for idx, item in subset_df.iterrows():
            point = Point(item.long, item.lat)
            #print(point)
            #print(f'Item long and lat are {item.long} {item.lat}')
            bounded_xy = []
            pierced = []
            #print(f'Shape of shape_df is {self.shape_df.shape}')
            filtered_shapes = self.shape_df[(self.shape_df.minx - offset < item.long) &
                           (self.shape_df.maxx + offset > item.long) &
                           (self.shape_df.miny - offset < item.lat) &
                           (self.shape_df.maxy + offset > item.lat)]
            #print(f'Shape of filtered_shapes is {filtered_shapes.shape}')
            for shapeID, shape in filtered_shapes.iterrows():
                polygon = shapely.wkt.loads(shape.polygon)
                print(f"Before within {polygon}")
                if point.within(polygon): #If it pierces the shape, add to the pierced list
                    print("In within")
                    if shapeID not in pierced:
                        pierced.append(shapeID)
                else: #otherwise add it to the bounded list
                    if shapeID not in bounded_xy:
                        bounded_xy.append(shapeID)
            #Not false positive or pierced
            if (len(pierced) == 0) and (filtered_shapes.shape[0]>0):
                nearest = nearest_neighbor(point, filtered_shapes)
                pierced.append(nearest)
                bounded_xy.remove(nearest)
            #Get counds of each list
            pierced_count = len(pierced)
                
            #Model results
            if pierced_count > 0:
                status = "Pierced" if (pierced_count==1) else "Pierced_Multiple"
            else:
                status = "Not Found"
            results.append({'TempIDZ':idx, f'{validator}_status':status,
                                f'{validator}_pierced_ShapeIDs':pierced})
            count+=1
        to_return = pd.DataFrame.from_dict(results)
        to_return.set_index('TempIDZ', inplace=True)
        to_return.index = to_return.index.astype(int)
        return(to_return)

    def get_failed_shapes(self):
        return self.failed_shapes
        
    def get_shapes(self):
        return self.shape_df
        
def nearest_neighbor(point, filtered_df):
    nearest_name = None
    nearest_distance = None
    for shapeID, row in filtered_df.iterrows():
        temp_shape = shapely.wkt.loads(row.polygon)
        temp_dist = point.distance(temp_shape)
        if nearest_name is None:
            nearest_name = shapeID
            nearest_distance = temp_dist
        elif temp_dist < nearest_distance:
            nearest_name = shapeID
            nearest_distance = temp_dist
    return nearest_name     

