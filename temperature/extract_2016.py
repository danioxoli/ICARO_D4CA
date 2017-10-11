# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 16:20:09 2017

@author: daniele oxoli - Politecnico di Milano
"""


import pandas as pd
import numpy as np

#open the input csv file as DataFrame by indiexing it on the time column

directory_in="your input path"
directory_out="your output path"

df = pd.read_csv(directory_in+'/input.csv')
 
df['datetime'] = pd.to_datetime(df.datetime) 
df.set_index('datetime', inplace=True)

#Remove coarse outliers and clean up stations with poor data amount

for col in list(df):
    df.loc[df[col] > 45 ] = np.nan
    df.loc[df[col] < -10 ] = np.nan

check = df.count()/ len(df)    
    
for i in range (0,len(check)):   
    column = check.index[i]    
    if check[i] < 0.80:
        del df[column]

# this is to apply a rolling median filtering  
# later on this dataframe is considered in parallel to the original one
        
roll = df.rolling(window=3,center=True).median()

# clean up stations having at least correlation factors (pairwise Pearson's coeff.) lower than a fixed value

f = df.corr().min()
g = roll.corr().min()

for i in range (0,len(f)):   
    column = f.index[i]   
    if f[i] < 0.75:
        del df[column]

for i in range (0,len(g)):   
    column = g.index[i]   
    if g[i] < 0.75:
        del roll[column]       

# Compute monthly averages

df_month = df.groupby(pd.TimeGrouper(freq='M')).mean()
df_month_roll = roll.groupby(pd.TimeGrouper(freq='M')).mean()


# Store resluts in a csv, transpose DataFrames can be join with, for example, a station shapefile

k = df_month.transpose()
h = df_month_roll.transpose()


k.to_csv(directory_out+"/output_month.csv")
h.to_csv(directory_out+"/output_month_roll.csv")    


