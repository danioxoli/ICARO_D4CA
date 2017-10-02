# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 15:22:13 2017

@author: utente
"""

from seasonal import fit_seasons, adjust_seasons
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

directory_in="your_input_folder_path"

df = pd.read_csv(directory_in+'/your_file.csv')
df = df.rename(columns={'column with timestamps': 'datetime'}) 
df.set_index('datetime', inplace=True)

alpha = 2 # std treshold Temperature anomalies (on residuals)

#-------
# detrend and deseasonalize of temperature

# slicing on time: e.g. 2012 - 2015

st = '2012-01-01 00:00:00'
en = '2015-12-31 00:00:00'

df_cut= pd.DataFrame(df[st:en])

# to check the completness of the sliced DataFrame series

compl_list_cut = {}
for column in df_cut:
    compl_list_cut.update({str(column) : float(df_cut[str(column)].count())/len(df_cut)})

# Seasonal Adjustment of the temeprature series - input = list of only numerics

s = []
t_s = []
j = 0

for i in df_cut['temperature_station_x']:
    if str(i) != 'nan':
        s.append(i)
        t_s.append(df.index[j])
    j=j+1
    
a = np.array(s)
 
seasons, trend = fit_seasons(a)
 
adjusted = adjust_seasons(a, seasons=seasons)
 
residual = adjusted - trend


#check anomalies position in time 

b = residual > np.std(residual)*alpha

j = 0
p_t = []
                     
for i in b:
    if i==True:
        p_t.append((s[j],t_s[j]))
    j=j+1

#anomalies in traffic, input = list of only numerics      

k = []
t_b = []
j = 0

for i in df_cut['accesses']:
    if str(i) != 'nan':
        k.append(i)
        t_b.append(df.index[j])
    j=j+1
    
g = np.array(k)

beta = df_cut['accesses'].quantile(q=0.98)

b = g > beta 

j = 0
p_a = []
                     
for i in b:
    if i==True:
        p_a.append((k[j],t_b[j]))
    j=j+1


# check for temp and traffic anomalies in the same day 
dayst = []

for i in p_t:
    dayst.append(i[1].split(' ')[0])
    
u_dayst = set(dayst)

daysa = []

for i in p_a:
    daysa.append(i[1].split(' ')[0])
    
u_daysa = set(daysa)

#get the days with anomalies using intersection

res = set(u_daysa).intersection(u_dayst)

print ('time period = '+str(st)+' - '+str(en))
print ('N. of hours with T anomalies > ' +str(alpha)+' * '+str(np.std(residual)) + ' = '+ str(len(p_t)))
print ('N. of of hours with Accesses anomalies > ' +str(beta) ' = '+ str(len(p_a)))
print ('N. of days with both T and Accesses anomalies = ' + str(len(res)))


#crete list of synchronous anomlies

new_p_a = []
for d in results:
    for a in p_a:
        if a[1].split(" ")[0] == d:
            new_p_a.append(a)


new_p_t = []
for d in results:
    for t in p_t:
        if t[1].split(" ")[0] == d:
            new_p_t.append(t)

#sort tuples by date
import operator
from operator import itemgetter

new_p_t.sort(key=itemgetter(1))
new_p_a.sort(key=itemgetter(1))

#group traffic anomalies by date
from datetime import datetime, timedelta

t_group = []
item = new_p_a[0]
t_subgroup = []
dat_0 = datetime.strptime(item[1], "%Y-%m-%d %H:%M:%S")
dt_0 = str(dat_0).split(" ")[0]
t_subgroup.append(item[1].split(" ")[0])
t_subgroup.append(item[1].split(" ")[1])


for item in new_p_a[1::]:
    dat =  datetime.strptime(item[1], "%Y-%m-%d %H:%M:%S")
    dt = str(dat).split(" ")[0]
    if dat != dat_0 + timedelta(hours=1):
        t_subgroup.append(str(dat_0).split(" ")[1])
        t_group.append(t_subgroup)
        t_subgroup = []
        t_subgroup.append(str(dat).split(" ")[0])
        t_subgroup.append(str(dat).split(" ")[1])
        dat_0 = dat
        dt_0 = dt
    else:
        if dt_0 == dt:
            dat_0 = dat
            dt_0 = dt
        else:
            t_subgroup.append(str(dat_0).split(" ")[1])
            t_group.append(t_subgroup)
            t_subgroup = []
            t_subgroup.append(str(dat).split(" ")[0])
            t_subgroup.append(str(dat).split(" ")[1])
            dat_0 = dat
            dt_0 = dt

#check if the last line of t_group contains the last recorded time and update it
item = new_p_a[-1]
ultimogiorno = datetime.strptime(item[1], "%Y-%m-%d %H:%M:%S")
ultimadata = str(ultimogiorno).split(" ")[0]
ultimaora = str(ultimogiorno).split(" ")[1]
if dt==ultimadata and ultimaora != dat_0 + timedelta(hours=1):
    t_subgroup.append(str(ultimaora).split(" ")[0])
    t_group.append(t_subgroup)

#add the temperature anomalies as delta hours since the beginning of the traffic anomalies
for item in t_group[::]:
    for a in new_p_t[::]:
        data = datetime.strptime(a[1], "%Y-%m-%d %H:%M:%S")
        giorno = str(data).split(" ")[0]
        ora = str(data).split(" ")[1]
        if item[0]==giorno:
            if ora>item[1]:
                ora_traffico=(item[0]+' '+item[1])
                ora_t_datetime=datetime.strptime(ora_traffico, "%Y-%m-%d %H:%M:%S")
                delta=data-ora_t_datetime
                delta_ore=divmod(delta.total_seconds(),3600)
                indice=t_group.index(item)
                t_group[indice].append(delta_ore[0])
    
# the list t_group contains datetime and duration of traffic anomalies and delta time of synchronous anomalies in temperature
# expressed in terms of delta time from the beginning of any traffic anomaly
