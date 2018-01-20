# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 11:19:59 2017
#
# Project:  ICARO - D4CA
# Purpose:  Convert MongoDB json WAZE data export into geojson Feature Collection for GIS processing
# Author:   Daniele Oxoli (daniele.oxoli@polimi.it)
# Affiliation: Dep. of Civil and Environmental Engineering, Politecnico di Milano, P.zza Leonardo da Vinci 32, 20133, Milano, Italy
#
"""

import os
import pandas as pd
import time
import json
import glob

# check how much time the script takes

start_time = time.clock()

#1ST STEP 
#split db json export file into sigle json files and saves them

directory_in="folderpath" #where you stored the separated json files
directory_out="folderpath" #where you you want to store the processed json file

#splitting db json file  

waze10 = pd.read_json("path to MongoDB data export.json")
s = pd.DataFrame()
for i in range(0,len(waze10.jams)):
    s = json.dumps(waze10.jams[i])
    with open(directory_in + "/jams%i.json" %i,"wb") as f:
        f.write(s)
        
print("split done")
        
#2ND STEP json files to dataframe 

# list of not interesting columns
col_to_remove = ['Unnamed: 0','blockingAlertUuid','turnType', 'type','segments', 'startNode','endNode']

time_conversion_function = lambda x: time.strftime('%Y-%m-%d %H:%M:%S',  time.gmtime(x/1000.))

#checking the files in the folder and converting them into dataframe
for f in os.listdir(directory_in):
    # print (f)
    statinfo = os.stat(directory_in+'/'+f) #checking size of the file to exclude empty files from the code
    if statinfo.st_size > 100:    
        df = pd.read_json(directory_in+'/'+f, )       
        
        # remove not useful columns 
        
        for column in list(df.columns):
            if column in col_to_delete:
                del df[column]            
        
        # let's remove empty row, in case their exist, for the main attributes i.e. "line","level" and 'pubMillis'
        
        df_clean = df.dropna(subset = ['line', 'level','pubMillis'])
        
        # apply time conversion for creating a new column "datetime"
        #the pubMillis is divide by 1000 to get it in seconds
        
        df_clean['datetime'] = df_clean['pubMillis'].apply(time_conversion_function)    
                
        #store the clean dataframe in a json or a csv (with json is faster)
        
        df_clean.to_json(directory_out+ '/'+ f.split('.')[0] + '.json', orient= 'records')
        #df_clean.to_cvs(directory_csv+ '/'+ f.split('.')[0] + '.csv', encoding = 'utf-8')

        
print("clean done")

# Create the single cleaned json file for next steps

result = []
for f in glob.glob(directory_out+ '/'+ "*.json"): # change *.json to *.csv if you are working with csv files
    with open(f, "rb") as infile:
        result.append(json.load(infile))

with open("path to the new merged file.json", "wb") as outfile:
     json.dump(result, outfile)

print('merge done')

end_time = time.clock()  

print ("processing time manipulation: "+ str(end_time - start_time))

'''-------------------------------------------------------------------------------------

now we have a clean set of jsons, containg the events at any call of the API, next step is to open one 
json per time, and put each event in a geojson feature collection 
'''

start_time = time.clock()

# read all events as cell of a dataframe (rows = API call, columns = N. of events registered) 

df1 = pd.read_json("path to the new merged file.json.json") 

# write the geojson file of all the events reading by row and column the dataframe

geoj= []
l = []
p = []
u = []
o = [4,5]

for i in range(0, len(df1)):
    for j in range(0, len(df1.columns)):
        
        # read single events and check if they are not empty (i.e they have value in the column j)
        # and they have the required level attribute
        
        event = df1[j][i]
        
        if type(event) != type(None) and event['level'] in o :
             
            # check if the event has been yet recorded, if yes go to the next event
            
            if event['uuid'] not in u:
                
                # create a list of unique id (uuid) to skip writing duplicate events in the final geojson            
                
                u.append(event['uuid'])
                
                # get a list of list of point coordinates belonging to the line feature
            
                for item in event['line']:
                    #print item
                    for coord in item:
                        p.append(item[coord])
                        
                    # need lon,lat but from the dataframe we have lat,lon so we change the order
                    
                    p_ord = [p[1],p[0]]
                    l.append(p_ord)
                    
                    # clean up the point coordinate list
                    
                    p = []
                    p_ord = []
                
                # write the geojson of the event using the dataframe information
                    
                event_gj= {'type': 'Feature',
                             'geometry': {
                             'type': 'LineString',
                             'coordinates': l
                          },
                        'properties': {
                          'uuid': event['uuid'],         
                          'city': event['city'],
                          'country': event['country'],
                          'roadType': event['roadType'],
                          'speed':  event['speed'],
                          'street': event['street'],          
                          'length': event['length'],
                          'delay':  event['delay'],         
                          'level':  event['level'],          
                          'pubMillis': event['pubMillis'],
                          'datetime': event['datetime']
                          }
                        },
            
                # add the geojson event to the full list of geojson events
                
                geoj.extend(event_gj)
                
                # clean up the event coordinate lists
                l = []
    
# write the full list of geojson events in a geojson collection
        
collection = {
    'type': 'FeatureCollection',
    'features': geoj
}        
  
# write the geojson collection into a geojson file

final_geoj = json.dumps(collection)

with open("path to the final file.geojson","wb") as f:
    f.write(final_geoj)


end_time = time.clock()  

print ("processing time: geojson creation: "+ str(end_time - start_time))
'''-----------------------------------------------------------------------------'''
