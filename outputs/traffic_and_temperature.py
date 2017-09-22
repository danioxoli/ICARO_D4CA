# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 15:22:13 2017

@author: utente
"""
#import os
#import datetime
#import csv

from seasonal import fit_seasons, adjust_seasons
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

directory_out="/Users/daniele/Desktop/ICARO"

df = pd.read_csv(directory_out+'/icaro.csv')
df = df.rename(columns={'Unnamed: 0': 'datetime'}) 
df.set_index('datetime', inplace=True)


#df_norm = (df - df.mean()) /df.std()
#df_norm.plot()
#sem = df_time_norm.sem()

compl_list = {}
for column in df:
    compl_list.update({str(column) : float(df[str(column)].count())/len(df)})

alpha = 2 # std treshold Temperature anomalies (on residuals)
beta = 3 # std treshold Traffic anomalies

#-------
# detrend and deseasonalize of temperature

s = []
t_s = []
j = 0

for i in df['tmp_5897']:
    if str(i) != 'nan':
        s.append(i)
        t_s.append(df.index[j])
    j=j+1
    
a = np.array(s)
 
seasons, trend = fit_seasons(a)
 
adjusted = adjust_seasons(a, seasons=seasons)
 
residual = adjusted - trend


#check anomalies position in time        

# b = residual > np.std(residual)*3 #using residuals

b = residual > np.std(residual)*alpha

j = 0
p_t = []
                     
for i in b:
    if i==True:
        p_t.append((s[j],t_s[j]))
    j=j+1

        
# visualize results
#plt.figure()
#plt.plot(s, label='data')
#plt.plot(trend, label='trend')
#plt.plot(residual, label='residual')
#plt.plot(seasons, label='seasons')
#plt.legend(loc='upper left')


#anomalies in traffic

k = []
t_b = []
j = 0

for i in df['accesses']:
    if str(i) != 'nan':
        k.append(i)
        t_b.append(df.index[j])
    j=j+1
    
g = np.array(k)


b = g > np.std(g)*beta 

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

#get the days with anomalies

results = set(u_daysa) & set(u_dayst)

#or using intersection

res = set(u_daysa).intersection(u_dayst)

print ('2012-2016')
print ('N. of days with T anomalies > ' +str(alpha)+' * '+str(np.std(residual)) + ' = '+ str(len(p_t)))
print ('N. of of days with Accesses anomalies > ' +str(beta)+' * '+str(np.std(g)) + ' = '+ str(len(p_a)))
print ('N. of days with T and Accesses anomalies = ' + str(len(res)))
print ('% agreement = ' + str(len(res)/float(len(p_t))))

'''-------------------------------------------------'''

# slicing in time: 2012 - 2015

st = '2012-01-01 00:00:00'
en = '2015-12-31 00:00:00'

df_cut= pd.DataFrame(df[st:en])

compl_list_cut = {}
for column in df_cut:
    compl_list_cut.update({str(column) : float(df_cut[str(column)].count())/len(df_cut)})

# detrend and deseasonalize of temperature

s = []
t_s = []
j = 0

for i in df_cut['tmp_5897']:
    if str(i) != 'nan':
        s.append(i)
        t_s.append(df_cut.index[j])
    j=j+1
    
a = np.array(s)
 
seasons, trend = fit_seasons(a)
 
adjusted = adjust_seasons(a, seasons=seasons)
 
residual = adjusted - trend

#check anomalies position in time        

# b = residual > np.std(residual)*3 #using residuals

b = residual > np.std(residual)*alpha

j = 0
p_t = []
                     
for i in b:
    if i==True:
        p_t.append((s[j],t_s[j]))
    j=j+1

        
# visualize results
#plt.figure()
#plt.plot(s, label='data')
#plt.plot(trend, label='trend')
#plt.plot(residual, label='residual')
#plt.plot(seasons, label='seasons')
#plt.legend(loc='upper left')


#anomalies in traffic

k = []
t_b = []
j = 0

for i in df_cut['accesses']:
    if str(i) != 'nan':
        k.append(i)
        t_b.append(df_cut.index[j])
    j=j+1
    
g = np.array(k)


b = g > np.std(g)*beta 

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

#get the days with anomalies

results = set(u_daysa) & set(u_dayst)

#or using intersection

res = set(u_daysa).intersection(u_dayst)

print ('2012-2015')
print ('N. of days with T anomalies > ' +str(alpha)+' * '+str(np.std(residual)) + ' = '+ str(len(p_t)))
print ('N. of of days with Accesses anomalies > ' +str(beta)+' * '+str(np.std(g)) + ' = '+ str(len(p_a)))
print ('N. of days with T and Accesses anomalies = ' + str(len(res)))
print ('% agreement = ' + str(len(res)/float(len(p_t))))

'''-------------------------------------------------'''

# slicing in time: 2016

st = '2016-01-01 00:00:00'
en = '2016-12-31 00:00:00'

df_cut2= pd.DataFrame(df[st:en])

compl_list_cut2 = {}
for column in df_cut2:
    compl_list_cut2.update({str(column) : float(df_cut2[str(column)].count())/len(df_cut2)})

# detrend and deseasonalize of temperature

s = []
t_s = []
j = 0

for i in df_cut2['tmp_5897']:
    if str(i) != 'nan':
        s.append(i)
        t_s.append(df_cut2.index[j])
    j=j+1
    
a = np.array(s)
 
seasons, trend = fit_seasons(a)
 
adjusted = adjust_seasons(a, seasons=seasons)
 
residual = adjusted - trend


#check anomalies position in time        

# b = residual > np.std(residual)*3 #using residuals

b = residual > np.std(residual)*alpha

j = 0
p_t = []
                     
for i in b:
    if i==True:
        p_t.append((s[j],t_s[j]))
    j=j+1

        
# visualize results
#plt.figure()
#plt.plot(s, label='data')
#plt.plot(trend, label='trend')
#plt.plot(residual, label='residual')
#plt.plot(seasons, label='seasons')
#plt.legend(loc='upper left')


#anomalies in traffic

k = []
t_b = []
j = 0

for i in df_cut2['accesses']:
    if str(i) != 'nan':
        k.append(i)
        t_b.append(df_cut2.index[j])
    j=j+1
    
g = np.array(k)

b = g > np.std(g)*beta 

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

#get the days with anomalies

results = set(u_daysa) & set(u_dayst)

#or using intersection

res = set(u_daysa).intersection(u_dayst)

print ('2016')
print ('N. of days with T anomalies > ' +str(alpha)+' * '+str(np.std(residual)) + ' = '+ str(len(p_t)))
print ('N. of of days with Accesses anomalies > ' +str(beta)+' * '+str(np.std(g)) + ' = '+ str(len(p_a)))
print ('N. of days with T and Accesses anomalies = ' + str(len(res)))
print ('% agreement = ' + str(len(res)/float(len(p_t))))







#crete new_p_a and new_p_t according to res dates
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

#controllo se l'ultima riga di t_group contiene l'ultima ora registrata e nel caso aggiorno
item = new_p_a[-1]
ultimogiorno = datetime.strptime(item[1], "%Y-%m-%d %H:%M:%S")
ultimadata = str(ultimogiorno).split(" ")[0]
ultimaora = str(ultimogiorno).split(" ")[1]
if dt==ultimadata and ultimaora != dat_0 + timedelta(hours=1):
    t_subgroup.append(str(ultimaora).split(" ")[0])
    t_group.append(t_subgroup)

#Aggiungo i picchi di temperatura indicandoli come differenza di ore dall'inizio del fenomeno di traffico
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
    







