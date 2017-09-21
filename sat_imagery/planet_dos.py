# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 17:00:26 2017
#
# Project:  ICARO - D4CA
# Purpose:  MERGE multiple tiles and perform ToA and DOS correction on PlanetScope Imagery 
#           (https://www.planet.com/docs/spec-sheets/sat-imagery)
# Author:   Daniele Oxoli, Monia Elisa Molinari (daniele.oxoli, moniaelisa.molinari@polimi.it)
# Affiliation: Dep. of Civil and Environmental Engineering, Politecnico di Milano, 
#              P.zza Leonardo da Vinci 32, 20133, Milano, Italy
#
"""
###############################################################################
# To automatically generate ToA and DOS and merge tile related to a specific area or time period
# (e.g. months of a year) you need to organize Planet imagery files in folder tree like this:
#  
#                       (Root Folder) 
#                           |
#  (Subfolder - Month 1),    (Subfolder - Month 2),   (Subfolder - Month 3) ...
#           |
#  (tile folder 1_Month 1),  (tile folder 2_Month 1),  ...
#           |
#  *1 <tilename>_AnalyticMS_DN_udm.tif
#  *2 <tilename>_AnalyticMS_metadata.xml  -> these are the image product you download from the Planet Explorer platform 
#  *3 <tilename>_AnalyticMS.tif              (https://www.planet.com/explorer) - mandatory file are 2 and 3
#  *4 <tilename>_metadata.json
#
# note: the image product name is generally composed of the following elements: 
# <acquisition date>_<acquisition time>_<satellite_id>_<productLevel><bandProduct>.<extension>
###############################################################################
'''
import dependncies and set the working paths
'''

import xml.etree.ElementTree as ET
import os
from osgeo import gdal 
import subprocess
import shutil
import glob

path = "<root folder path>" #path of Planet imagery root folder as explained above
gdal_merge_path="path to gdal_merge.py" # this Python script can be download here: 
                                        # https://svn.osgeo.org/gdal/trunk/gdal/swig/python/scripts/gdal_merge.py 
  
# if you are working under Window you may chnge the path to the temporary folder from "/tmp" to "%USERPROFILE%\AppData\Local\"
# and check for issues due to backslash. We strongly suggest to test this script using as OS the OSGeo Live VM 
# (https://live.osgeo.org) to work around dependecies issues.
###############################################################################
'''
# A * From Digital Numbers to Top of Atmosphere (ToA) Reflectance:
'''
#define xml abbreviations
ps="{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}"
eop="{http://earth.esa.int/eop}"
gml="{http://www.opengis.net/gml}"
opt="{http://earth.esa.int/opt}"

#initialise final dictionary
d = {} 

#loop on root folder, months folder and months folder files (.xml)
for root, dirs, files in os.walk(path):  
    for name in files:
        if name.endswith((".xml")) and not name.startswith(('.')):
            print (name)
#           parse the xml files        
            data = ET.parse(root+ "/" + name)
            tags = data.getroot()
            
#           initialise single image sub-dictionary 
            d_temp = {name.split('_metadata')[0]:{'rc_b1': '', 'rc_b2': '', 'rc_b3': '','rc_b4': ''}}           
                    
#           fill single image sub-dictionary with respective reflectance coeff for each band                  
            for member in tags.findall(gml+'resultOf'):              
                for submember in member.findall(ps+'EarthObservationResult'):
                    for info in submember.findall(ps+'bandSpecificMetadata'):                   
                        band = info.find(ps+'bandNumber').text
                        rf = info.find(ps+'reflectanceCoefficient').text
#                       update the single image sub-dictionary with reflectance coeff                     
                        d_temp[name.split('_metadata')[0]]['rc_b'+band] = rf
                        
#           update final dictionary
            d.update(d_temp)           
            
            os.mkdir("/tmp/%s"%name.split('_metadata')[0]) # create temporary folder          
            tmpfolderName = "/tmp/%s"%name.split('_metadata')[0]
            print tmpfolderName
            
            # do bandwise ToA Reflectance correction           
            ds = gdal.Open(root+ "/" + name.split('_metadata')[0]+'.tif')
            for b in range(ds.RasterCount+1)[1::]:
                raster_band = ds.GetRasterBand(b)
                raster_arr = raster_band.ReadAsArray()
                [cols, rows] = raster_arr.shape
                print b
                print float(d[name.split('_metadata')[0]]['rc_b%s'%b])
                raster_new_arr = raster_arr*float(d[name.split('_metadata')[0]]['rc_b%s'%b])
                driver = gdal.GetDriverByName("GTiff")
                outdata = driver.Create("%s/%s_%s.tiff"%(tmpfolderName,name.split('_metadata')[0],b), rows, cols, 1, gdal.GDT_Float32)
                outdata.SetGeoTransform(ds.GetGeoTransform()) #sets same geotransform as input
                outdata.SetProjection(ds.GetProjection()) #sets same projection as input
                outband = outdata.GetRasterBand(1)
                outband.WriteArray(raster_new_arr)
                outband.FlushCache() #saves to disk!!
                outdata = None
                outband=None
            ds = None
             
            # Merge single bands to a multiband image                  
            merge_command_1 = ["python", "%s/gdal_merge.py"%gdal_merge_path,"-separate", "-o", "%s_TOA.tiff"%(root+ "/" + name.split('_metadata')[0])]
            merge_command_2 = sorted(glob.glob(tmpfolderName+"/*.tiff"))  # get the files to merge in temporary folder
             
            merge_command_toa = merge_command_1 + merge_command_2
            print merge_command_toa

            subprocess.call(merge_command_toa) # call gdal_merge.py command and save output in the input folder
            shutil.rmtree(tmpfolderName) # remove temporary folder

###############################################################################
'''
# B * Merge mouthly tiles:
'''

#loop on root folder, months folder and months folder files (_TOA.tiff)
for item in os.listdir(path):
    print item
    l = []
    for root, dirs, files in os.walk(path+'/'+item):  
        for name in files:
            if name.endswith(("_TOA.tiff")):        
                l.append(root +'/'+ name)

    merge_command_3 = ["python", gdal_merge_path + "/gdal_merge.py","-n", "0.0","-a_nodata", "0.0", "-o", path+item+"_M.tiff"] 
    merge_command_4 = l
    merge_command_merge = merge_command_3 + merge_command_4
    subprocess.call(merge_command_merge)
    print ("merged: "+ item)

###############################################################################    
'''
# C * Dark Object Subtraction (DOS):
'''

#loop on root folder files (_M.tiff)
for item in os.listdir(path):
    if item.endswith(("_M.tiff")):
        os.mkdir("/tmp/%s"%item.split('_M.tiff')[0]) # create temporary folder          
        tmpfolderName = "/tmp/%s"%item.split('_M.tiff')[0]
        
        ds = gdal.Open(path+'/%s'%item)
        
        print (path+'/%s'%item + ' this is the file to open')
    
        # do bandwise subtraction of min(band) to any _M.tiff images
        for b in range(ds.RasterCount+1)[1::]:
            
            raster_band = ds.GetRasterBand(b)
            raster_arr = raster_band.ReadAsArray()           
            [cols, rows] = raster_arr.shape
            print b
            stat = raster_band.GetStatistics(True, True)
            b_min = stat[0]
            print b_min

            raster_new_arr = raster_arr - b_min
            raster_zero_arr =  raster_new_arr.clip(0.0)
            driver = gdal.GetDriverByName("GTiff")
            outdata = driver.Create("%s/%s_%s.tiff"%(tmpfolderName,item.split('_M.tiff')[0],b), rows, cols, 1, gdal.GDT_Float32)
            outdata.SetGeoTransform(ds.GetGeoTransform()) #sets same geotransform as input
            outdata.SetProjection(ds.GetProjection()) #sets same projection as input
            outband = outdata.GetRasterBand(1)
            outband.WriteArray(raster_zero_arr)
            outband.FlushCache() ##saves to disk!!
            outdata = None
            outband=None
        ds = None
             
        # Merge single bands to a multiband image       
        merge_command_5 = ["python", "%s/gdal_merge.py"%gdal_merge_path, "-separate","-o", "%s/%s_DOS.tiff"%(path,item.split('_M.tiff')[0])]
        merge_command_6 = sorted(glob.glob(tmpfolderName+"/*.tiff")) # get the files to merge in temporary folder
             
        merge_command_dos = merge_command_5 + merge_command_6
        print merge_command_dos

        subprocess.call(merge_command_dos) # call gdal_merge.py command and save output in the input folder
        shutil.rmtree(tmpfolderName) # remove temporary folder

###############################################################################
'''
 Now you are ready to start classification!
 Running this code may take time depending on your hardware equipment
'''


