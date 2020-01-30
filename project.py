#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Importing Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium

# Loading data
dateparse = lambda x: pd.datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p')
data = pd.read_csv('Pedestrian_volume__updated_monthly_.csv',parse_dates=['Date_Time'], date_parser=dateparse)

# data info
data.shape
data.info()
data.head()

# Missing Values and their number
data.columns[data.isnull().any()] 

Nnull = data.isnull().sum()/len(data)*100
Nnull = Nnull[Nnull>0]
Nnull.sort_values(inplace=True, ascending=False)
print(Nnull)

# EDA
data['Month'] = pd.Categorical(data['Month'], categories = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                                                            'August', 'September', 'October', 'November','December'], ordered = True)

data.groupby('Year')['Hourly_Counts'].mean().plot.bar()

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July','August', 'September', 'October', 'November','December']
plt.figure(figsize=(12,6))
data.groupby('Month')['Hourly_Counts'].mean().plot(marker = 'o')
plt.xticks(np.arange(12), months)
plt.ylabel('Pedestrian Count')
plt.show()

data.groupby('Month')['Hourly_Counts'].mean().plot.bar()

days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday']
data['Day'] = pd.Categorical(data['Day'],categories=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday'], ordered=True)
plt.figure(figsize=(8,4))
data.groupby('Day')['Hourly_Counts'].mean().plot(marker='o')
plt.xticks(np.arange(7), days)
plt.ylabel('Hourly Counts')
plt.show()

temp=data.groupby('Sensor_Name')['Hourly_Counts'].mean().sort_values(ascending=False)
plt.figure(figsize=(16,8))
temp.plot(kind='bar',color='red')
plt.ylabel('Hourly_Counts')
plt.show()

import datetime
def applyer(row):
    if row == 'Saturday' or row == 'Sunday':
        return 1
    else:
        return 0

temp2 = data['Day'].apply(applyer)
data['weekend']=temp2

data.groupby('weekend')['Hourly_Counts'].mean().plot.bar()

plt.figure(figsize=(10,6))
data.loc[data['Day'] == 'Monday'].groupby('Time')['Hourly_Counts'].mean().plot(marker = 'o', color = 'red', label = 'Mon')
data.loc[data['Day'] == 'Tuesday'].groupby('Time')['Hourly_Counts'].mean().plot(marker = 'o', color = 'blue', label = 'Tue')
data.loc[data['Day'] == 'Wednesday'].groupby('Time')['Hourly_Counts'].mean().plot(marker = 'o', color = 'green',label = 'Wed')
data.loc[data['Day'] == 'Thursday'].groupby('Time')['Hourly_Counts'].mean().plot(marker = 'o', color = 'black', label = 'Thu')
data.loc[data['Day'] == 'Friday'].groupby('Time')['Hourly_Counts'].mean().plot(marker = 'o', color = 'yellow', label = 'Fri')
data.loc[data['Day'] == 'Saturday'].groupby('Time')['Hourly_Counts'].mean().plot(marker = 'o', color = 'orange', label = 'Sat')
data.loc[data['Day'] == 'Sunday'].groupby('Time')['Hourly_Counts'].mean().plot(marker = 'o', color = 'pink', label = 'Sun')
plt.legend()
plt.show()

daytime = data[(data['Sensor_Name']=='Flinders St-Swanston St (West)') ][['Time','Day','Hourly_Counts']].groupby(['Time','Day']).mean().unstack('Day')
plt.figure(figsize=(8,8))
sns.heatmap(daytime)

# Loading sensor location data and merging two dataframes
sensor_location = pd.read_csv('Pedestrian_sensor_locations.csv')
sensor_location.head()

sensor_location['Sensor_ID'] = sensor_location['Sensor ID']
sensor_location = sensor_location.drop(['Sensor ID', 'Sensor Description','Sensor Name', 'Status', 'Upload Date', 'Location Type', 'Geometry'], 1)

merge_data = data.merge(sensor_location, on = 'Sensor_ID')

# grouping by sensor locations to plot on map
locations = merge_data.groupby(['Sensor_Name','Sensor_ID', 'Latitude', 'Longitude'],as_index = False)['Hourly_Counts'].mean()

def plot_location_count(locations):
    melbourne_map = folium.Map(location=[-37.814, 144.96332], zoom_start=14, tiles="OpenStreetMap")
    for index, row in locations.iterrows():
        lat = row['Latitude']
        long = row['Longitude']
        popup_text = """Hourly_Counts : {}<br>
                    Sensor Description : {}<br>"""
        popup_text = popup_text.format(row['Hourly_Counts'],row['Sensor_Name'])
        radius = row['Hourly_Counts']/100
        folium.CircleMarker(location = [lat, long], radius = radius, popup= popup_text, fill = True).add_to(melbourne_map)
    return melbourne_map

folium_map = plot_location_count(locations)
folium_map.save("map.html")