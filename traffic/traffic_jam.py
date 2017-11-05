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

#1ST STEP (working)
#working code to separate multiple json files into unique json files and saves them
 
#separating json of database 

waze10 = pd.read_json("C:/Users/utente/Desktop/dilek/waze_events_2000.json")
s = pd.DataFrame()
for i in range(0,len(waze10.jams)):
    s = json.dumps(waze10.jams[i])
    with open("C:/Users/utente/Desktop/dilek/in10/jams%i.json" %i,"wb") as f:
        f.write(s)
        
print("split done")
        
#2ND STEP json csv conversion (working)

directory_in="C:/Users/utente/Desktop/dilek/in10" #where you stored the separated json files
directory_out="C:/Users/utente/Desktop/dilek/out10" #where you you want to store the processed json file


# list of not useful columns
col_to_delate = ['Unnamed: 0','blockingAlertUuid','turnType', 'type','segments', 'startNode','endNode']

time_conversion_function = lambda x: time.strftime('%Y-%m-%d %H:%M:%S',  time.gmtime(x/1000.))


#checking the files in the folder and converting them into dataframe
for f in os.listdir(directory_in):
    # print (f)
    statinfo = os.stat(directory_in+'/'+f) #checking size of the file to exclude empty files from the code
    if statinfo.st_size > 100:    
        df = pd.read_json(directory_in+'/'+f, )       
        
        # remove not useful columns (maybe we can remove more but like that seems enough)
        
        for column in list(df.columns):
            if column in col_to_delate:
                del df[column]            
        
        # let's remove empty row, in case their exist, for the main attributes i.e. "line","level" and 'pubMillis'
        
        df_clean = df.dropna(subset = ['line', 'level','pubMillis'])
        
        # apply time conversion for creating a new column "datetime"
        #the pubMillis is divide by 1000 to get it in seconds
        
        df_clean['datetime'] = df_clean['pubMillis'].apply(time_conversion_function)    
                
        #this is to store the clean dataframe in a json or a csv (with json is faster)
        
        df_clean.to_json(directory_out+ '/'+ f.split('.')[0] + '.json', orient= 'records')
        #df_clean.to_cvs(directory_csv+ '/'+ f.split('.')[0] + '.csv', encoding = 'utf-8')

        
print("clean done")
            
result = []
for f in glob.glob(directory_out+ '/'+ "*.json"):
    with open(f, "rb") as infile:
        result.append(json.load(infile))

with open("C:/Users/utente/Desktop/dilek/merged_file10.json", "wb") as outfile:
     json.dump(result, outfile)

print('merge done')

end_time = time.clock()  

print ("processing time manipulation: "+ str(end_time - start_time))

'''-------------------------------------------------------------------------------------

now we have a clean set of json, containg the events at any call of the API, next step is to open one 
json per time, and put any event in geojson feature collection ->  let's go!

'''

start_time = time.clock()

# read al events as cell of a dataframe (rows = API call, columns = N. of events registered) 

df1 = pd.read_json("C:/Users/utente/Desktop/dilek/merged_file.json") 


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
                
                # create a list of unique id (uuid) to skip writing duplicates event in the final geojson            
                
                u.append(event['uuid'])
                
                # get a list of list of point coordinate belonging to the line feature
            
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
                
                # write the geojason of the event using the dataframe information
                    
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
            
                # add the geojason event to the full list of geojson events
                
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

with open("C:/Users/utente/Desktop/dilek/split/final_geoj4_5.geojson","wb") as f:
    f.write(final_geoj)


end_time = time.clock()  

print ("processing time: geojson creation: "+ str(end_time - start_time))
'''-----------------------------------------------------------------------------'''