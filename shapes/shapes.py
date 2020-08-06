# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 10:10:38 2020

@author: fisherd
"""
import numpy as np
import pandas as pd
from shapely.geometry import Point#, Polygon
from shapely.geos import WKTReadingError #Needed for new error
import shapely.wkt
import time

class ShapesList():
    
    def __init__(self, file):
        shape_frame = pd.read_csv(file)
        shape_frame.dropna(inplace=True)
        shape_frame['PARCEL_APN'] = shape_frame['PARCEL_APN'].round(0).astype(np.int64)
        shape_frame.drop_duplicates(inplace=True)
        shapes = []
        self.failed_shapes = []
        
        #For each shape, change to polygon, and get min/max coords. Append to list of dictionaries
        for idx, item in shape_frame.iterrows():
            try:
                #print(idx)
                polygon = shapely.wkt.loads(item.GEOM)
                minx, miny, maxx, maxy = polygon.bounds
                shapes.append({'shapeID':item.PARCEL_APN, 'polygon':item.GEOM,
                               'minx':minx, 'maxx':maxx, 'miny': miny, 'maxy':maxy})
            except WKTReadingError:
                self.failed_shapes.append(idx)
        
        #Create dataframe for shapes, this time with min/max
        #We can probably do this with a .apply() method, but the above loop was clear enough.
        self.shape_df = pd.DataFrame.from_dict(shapes)
        
    def process_df(self,complete_df:pd.DataFrame, validator:str, offset:float = 0):
        print(f'Processing for {validator}')
        results = []
        subset_df = complete_df[['TempIDZ','PARCEL_APN',f'{validator}_long',f'{validator}_lat']]
        subset_df['PARCEL_APN'] = subset_df['PARCEL_APN'].round(0).astype(np.int64)
        
        subset_df.columns = ['TempIDZ','PARCEL_APN','long','lat']
        count = 0
        for idx, item in subset_df.iterrows():
            #print(f'\n\n\n{item.PARCEL_APN}')
            point = Point(item.long, item.lat)
            bounded_xy = []
            pierced = []
            filtered_shapes = self.shape_df[(self.shape_df.minx - offset < item.long) &
                           (self.shape_df.maxx + offset > item.long) &
                           (self.shape_df.miny - offset < item.lat) &
                           (self.shape_df.maxy + offset > item.lat)]
            #print(f'Filtered shapes are {filtered_shapes}')
            #print(f'Total of {filtered_shapes.shape[0]}')
            #Test for piercing and boundedness
            for i, shape in filtered_shapes.iterrows():
                polygon = shapely.wkt.loads(shape.polygon)
                if point.within(polygon): #If it pierces the shape, add to the pierced list
                    #print("Pierced")
                    if shape.shapeID not in pierced:
                        pierced.append(shape.shapeID)
                else: #otherwise add it to the bounded list
                    #print("Bounded")
                    if shape.shapeID not in bounded_xy:
                        bounded_xy.append(shape.shapeID)
                #print(f'Pierced shapes are {pierced}')
                #print(f'Bounded shapes are {bounded_xy}')
            #Not false positive or pierced
            if (len(pierced) == 0) and (filtered_shapes.shape[0]>0):
                nearest = nearest_neighbor(point, filtered_shapes)
                #print(f'Nearest is {nearest}')
                pierced.append(nearest)
                bounded_xy.remove(nearest)
            
                
            #Get counds of each list
            pierced_count = len(pierced)
                
            #Model results
            if item.PARCEL_APN in pierced:
                if pierced_count == 1:
                    status = "Pierced"
                else:
                    status = "Pierced_Multiple"
            elif pierced_count > 0:
                status = "False Positive"
            elif item.PARCEL_APN in bounded_xy:
                status = "Bounded_xy"
            else:
                status = "Not Found"
            #print(status)
            results.append({'TempIDZ':item.TempIDZ, f'{validator}_status':status,
                                f'{validator}_Pierced_APNs':pierced})
            count+=1
    

        to_return = pd.DataFrame.from_dict(results)
        return(to_return)
        
    def process_df_no_APN(self,complete_df:pd.DataFrame, validator:str, offset:float = 0):
        print(f'Processing for {validator}')
        results = []
        subset_df = complete_df[['TempIDZ',f'{validator}_long',f'{validator}_lat']]
        subset_df.columns = ['TempIDZ','long','lat']
        count = 0
        for idx, item in subset_df.iterrows():
            #print(f'\n\n\n{item.PARCEL_APN}')
            point = Point(item.long, item.lat)
            bounded_xy = []
            pierced = []
            filtered_shapes = self.shape_df[(self.shape_df.minx - offset < item.long) &
                           (self.shape_df.maxx + offset > item.long) &
                           (self.shape_df.miny - offset < item.lat) &
                           (self.shape_df.maxy + offset > item.lat)]

            for i, shape in filtered_shapes.iterrows():
                polygon = shapely.wkt.loads(shape.polygon)
                if point.within(polygon): #If it pierces the shape, add to the pierced list
                    #print("Pierced")
                    if shape.shapeID not in pierced:
                        pierced.append(shape.shapeID)
                else: #otherwise add it to the bounded list
                    #print("Bounded")
                    if shape.shapeID not in bounded_xy:
                        bounded_xy.append(shape.shapeID)
                #print(f'Pierced shapes are {pierced}')
                #print(f'Bounded shapes are {bounded_xy}')
            #Not false positive or pierced
            if (len(pierced) == 0) and (filtered_shapes.shape[0]>0):
                nearest = nearest_neighbor(point, filtered_shapes)
                #print(f'Nearest is {nearest}')
                pierced.append(nearest)
                bounded_xy.remove(nearest)
            
                
            #Get counds of each list
            pierced_count = len(pierced)
                
            #Model results
            if pierced_count > 0:
                status = "Pierced" if (pierced_count==1) else "Pierced_Multiple"
            else:
                status = "Not Found"
            #print(status)
            results.append({'TempIDZ':item.TempIDZ, f'{validator}_status':status,
                                f'{validator}_Pierced_APNs':pierced})
            count+=1
        to_return = pd.DataFrame.from_dict(results)
        return(to_return)

    def get_failed_shapes(self):
        return self.failed_shapes
        
    def get_shapes(self):
        return self.shape_df
        
def nearest_neighbor(point, filtered_df):
    nearest_name = None
    nearest_distance = None
    for index, row in filtered_df.iterrows():
        temp_shape = shapely.wkt.loads(row.polygon)
        temp_dist = point.distance(temp_shape)
        if nearest_name is None:
            nearest_name = row.shapeID
            nearest_distance = temp_dist
        elif temp_dist < nearest_distance:
            nearest_name = row.shapeID
            nearest_distance = temp_dist
    return nearest_name     

