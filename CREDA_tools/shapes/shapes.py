# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 10:10:38 2020

@author: fisherd
"""

import logging
import pandas as pd
from shapely.geometry import Point#, Polygon
from shapely.geos import WKTReadingError #Needed for new error
import shapely.wkt

import buildingid.code as bc

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)

#filehandler = logging.FileHandler('CREDA_run.log')
#filehandler.setLevel(logging.DEBUG)

#streamhandler = logging.StreamHandler()

#logger.addHandler(filehandler)
#logger.addHandler(streamhandler)

def unpack(WKT_object):
    if WKT_object.geom_type != 'Polygon':
        return_list = []
        WKT_list = list(WKT_object)
        for WKT in WKT_list:
            return_list.extend(unpack(WKT))
        return return_list
    else:
        return [WKT_object]
    
def get_UBID(polygon):
    polygon_WKT = shapely.wkt.loads(polygon)
    minx, miny, maxx, maxy = polygon_WKT.bounds
    centerx, centery = (polygon_WKT.centroid.coords)[0]
    UBID = bc.encode(latitudeLo=miny, longitudeLo=minx, latitudeHi=maxy, 
                                     longitudeHi=maxx, latitudeCenter=centery,
                                     longitudeCenter=centerx, codeLength=16)
    return UBID
        

class ShapesList():
    
    flags = pd.DataFrame(columns = ['Shape_Flag','ShapeID']).set_index('ShapeID')
    
    def __init__(self, file):
        shape_frame = pd.read_csv(file)
        shape_frame.dropna(inplace=True) # TODO Currently drops if incomplete info. Likely a problem
        shape_frame.drop_duplicates(inplace=True)
        shapes = []
        flags = []
        ShapeIDZ = 0
        
        if 'PARCEL_APN' in shape_frame.columns:
            pass
            '''
            if 'ShapeID' in shape_frame.columns:
                #logger.warning('PARCEL_APN and ShapeID present. PARCEL_APN retained as data')
            else:
                #logger.info('PARCEL_APN used for ShapeID')
                shape_frame.rename(columns={'PARCEL_APN':'ShapeID'})
            '''
        #For each shape, change to polygon, and get min/max coords. Append to list of dictionaries
        for idx, item in shape_frame.iterrows():
            if 'ShapeID' in shape_frame.columns:
                index = item.ShapeID
            else:
                index = idx
            try:
                WKT = shapely.wkt.loads(item.GEOM)
                WKT_shapes = unpack(WKT)
                if len(WKT_shapes) > 1:
                    flags.append({'ShapeID':index,'flag':'ShpInf_01'})
                for polygon in WKT_shapes:
                    minx, miny, maxx, maxy = polygon.bounds
                    shapes.append({'ShapeID':index, 'ShapeIDZ':ShapeIDZ, 'polygon':polygon.to_wkt(),
                                   'minx':minx, 'maxx':maxx, 'miny': miny, 'maxy':maxy,})
                    ShapeIDZ = ShapeIDZ + 1
            except WKTReadingError:
                flags.append({'ShapeID':index,'flag':'ShpErr_01'})
                #logger.exception(f'shapeID {index} failed parsing')
                
        #logger.info("In init creating shape_df")
        #Create dataframe for shapes, this time with min/max
        #We can probably do this with a .apply() method, but the above loop was clear enough.
        self.shape_df = pd.DataFrame.from_dict(shapes)
        self.shape_df.set_index('ShapeIDZ', inplace=True)
        if len(flags) > 0:
            self.flags = pd.DataFrame.from_dict(flags).set_index('ShapeID')
            self.flags = pd.merge(self.flags, self.Error_Codes, how='left', left_on='flag', right_index=True)
            self.flags['Shape_Flag'] = self.flags.flag + ": " + self.flags.description
            self.flags.drop(columns=['flag','description'], inplace=True)
        
        #self.flags['flag2'] = self.flags['flag'].str + " " + self.Error_Codes[self.flags.flag]
        '''
        for shape in list(self.failed_shapes.ShapeID):
            self.ShapeID_flags.setdefault(self.ShapeID, []).append("WKT didn't parse correctly")
        '''
        
    def process_df(self,complete_df:pd.DataFrame, validator:str, offset:float = 0):
        #logger.info(f'\tProcessing for {validator}')
        results = []
        subset_df = complete_df[[f'{validator}_long',f'{validator}_lat']]
        subset_df.columns = ['long','lat']
        count = 0
        for idx, item in subset_df.iterrows():
            point = Point(item.long, item.lat)
            bounded_xy = []
            pierced = []
            filtered_shapes = self.shape_df[(self.shape_df.minx - offset < item.long) &
                           (self.shape_df.maxx + offset > item.long) &
                           (self.shape_df.miny - offset < item.lat) &
                           (self.shape_df.maxy + offset > item.lat)]
            for ShapeIDZ, shape in filtered_shapes.iterrows():
                polygon = shapely.wkt.loads(shape.polygon)
                if point.within(polygon): #If it pierces the shape, add to the pierced list
                    if ShapeIDZ not in pierced:
                        pierced.append(ShapeIDZ)
                else: #otherwise add it to the bounded list
                    if ShapeIDZ not in bounded_xy:
                        bounded_xy.append(ShapeIDZ)
            pierced_count = len(pierced)
                
            #Model results
            if pierced_count > 0:
                status = "Pierced" if (pierced_count==1) else "Pierced_Multiple"
            elif filtered_shapes.shape[0]>0:
                nearest = nearest_neighbor(point, filtered_shapes)
                pierced.append(nearest)
                status="Nearest_Neighbor"
            else:
                status = "Not Found"

            results.append({'TempIDZ':idx, f'{validator}_status':status,
                                f'{validator}_pierced_ShapeIDZs':pierced})
            
            count+=1
        to_return = pd.DataFrame.from_dict(results)
        to_return.set_index('TempIDZ', inplace=True)
        to_return.index = to_return.index.astype(int)
        
        return(to_return)

    Error_Codes = {
        'ShpErr_01':'Bad WKT String',
        'ShpInf_01':'Multipolygon Found',
        'ShpInf_02':'Large Shape',
        'ShpInf_03':'Outside continental US'
        }
    Error_Codes = pd.DataFrame.from_dict(Error_Codes,orient='index', columns=['description'])
        
    def get_shapes(self):
        return self.shape_df

        
def nearest_neighbor(point, filtered_df):
    nearest_name = None
    nearest_distance = None
    for ShapeID, row in filtered_df.iterrows():
        temp_shape = shapely.wkt.loads(row.polygon)
        temp_dist = point.distance(temp_shape)
        if nearest_name is None:
            nearest_name = ShapeID
            nearest_distance = temp_dist
        elif temp_dist < nearest_distance:
            nearest_name = ShapeID
            nearest_distance = temp_dist
    return nearest_name     

