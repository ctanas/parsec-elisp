#!/usr/bin/env python3

import sys
import sgp4
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

# conj.py NORAD-ID1 NORAD-ID2 TIME1 TIMEDELTA
#           1         2         3     4

session = requests.Session()

def connect_to_st():
    print("Connecting to connect to space-track.org...")
    # this file should contain username and password
    with open('secrets.txt', 'r') as file:
        sec_lines = file.readlines()
        st_username = sec_lines[0].strip()
        st_password = sec_lines[1].strip()
    file.close()
    # avoiding connecting multiple times
    global session
    if not session:
        session = requests.Session()
    login_url = "https://www.space-track.org/ajaxauth/login"
    login_data = {"identity": st_username, "password": st_password}
    login_response = session.post(login_url, data=login_data)
    if login_response.status_code == 200:
        print("Login successful.")
    else:
        print("Login failed :-(")
    session_cookies = login_response.cookies
connect_to_st()

url_gp1_query = 'https://www.space-track.org/basicspacedata/query/class/gp_history/NORAD_CAT_ID/'+sys.argv[1]+'/EPOCH/>'+sys.argv[3]+'/orderby/EPOCH desc/limit/1/emptyresult/show'
url_gp2_query = 'https://www.space-track.org/basicspacedata/query/class/gp_history/NORAD_CAT_ID/'+sys.argv[2]+'/EPOCH/>'+sys.argv[3]+'/orderby/EPOCH desc/limit/1/emptyresult/show'
df_gp1 = pd.read_json(session.get(url_gp1_query).text)
df_gp2 = pd.read_json(session.get(url_gp2_query).text)

print(df_gp2)

tle1a = df_gp1.iloc[0]['TLE_LINE1']
tle1b = df_gp1.iloc[0]['TLE_LINE2']

tle2a = df_gp2.iloc[0]['TLE_LINE1']
tle2b = df_gp2.iloc[0]['TLE_LINE2']

# Convert TLEs to sgp4 objects
satellite1 = twoline2rv(tle1a.strip(), tle1b.strip(), wgs72)
satellite2 = twoline2rv(tle2a.strip(), tle2b.strip(), wgs72)

# Start and end dates (in UTC)
start_date = datetime.strptime(sys.argv[3], "%Y-%m-%d")
end_date = start_date + timedelta(days=int(sys.argv[4]))
time_difference = end_date - start_date
seconds_difference = time_difference.total_seconds()

# Step of iteration (in minutes)
step = 0.05
iterations = round(seconds_difference / step)

print("Data loaded for objects "+str(df_gp1.iloc[0]['NORAD_CAT_ID'])+" and "+str(df_gp2.iloc[0]['NORAD_CAT_ID']))
print(str(df_gp1.iloc[0]['OBJECT_NAME']))
print(str(df_gp2.iloc[0]['OBJECT_NAME']))
print("Begining "+str(iterations)+" iterations")
print("Steps: "+str(step)+" seconds")

x = 0
df2plot = pd.DataFrame()

# Find the closest approach between the two objects in the specified time period
closest_approach = None
min_distance = float('inf')
time_step = timedelta(seconds=step)
current_time = start_date
results = []
while current_time <= end_date:
    position1, velocity1 = satellite1.propagate(current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)
    position2, velocity2 = satellite2.propagate(current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)
    distance = ((position1[0] - position2[0])**2 + (position1[1] - position2[1])**2 + (position1[2] - position2[2])**2)**0.5
    if x % 1000 == 0: 
        new_row = {'time': current_time, 'dist': distance}
        df2plot = df2plot.append(new_row, ignore_index=True)
    if distance < min_distance:
        min_distance = distance
        closest_approach = current_time
    current_time += time_step
    print(" \%done: "+str(round(x/iterations*100)), end='\r')
    x+=1

print("Closest approach: ", closest_approach)
print("Distance: ", round(min_distance, 2), "km")

df2plot.plot(x='time', y='dist', kind='line')
plt.show()