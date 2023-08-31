#!/usr/bin/env python3

import sys
import os.path
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil.parser import parse as parsedate
from dateutil.relativedelta import relativedelta

# NORAD IDs to be monitored
norad_cat = sys.argv[1:]

# setting the time intervals: monthly and weekly
now = datetime.now()
last_month_date = now + relativedelta(months=-1)
last_month_date = str(last_month_date).split(" ")[0]
last_week_date = now + relativedelta(weeks=-1)
last_week_date = str(last_week_date).split(" ")[0]

# Authentification with space-track.org
with open('secrets.txt', 'r') as file:
    sec_lines = file.readlines()
    st_username = sec_lines[0].strip()
    st_password = sec_lines[1].strip()
file.close()
session = requests.Session()
login_url = "https://www.space-track.org/ajaxauth/login"
login_data = {"identity": st_username, "password": st_password}
login_response = session.post(login_url, data=login_data)
# Only display a message if an error is encountered
if login_response.status_code != 200:
    print("Login failed :-(")
    quit()
session_cookies = login_response.cookies

# Initializing some lists:
# Raw data list
df_list = []
# Apogee and perigee data
df_to_plot_m = []
df_to_plot_w = []
# List of Object Names
list_objects = []
# Columns to select from raw data, for plotting
columns_to_select = ['EPOCH', 'PERIAPSIS', 'APOAPSIS']

# Iteratively getting data from space-track.org, for the maximum interval (1 month)
for i in norad_cat:
    
    # Fetching data
    print("Fetching plotting data for: ", i)
    st_query = 'https://www.space-track.org/basicspacedata/query/class/gp_history/EPOCH/>'+str(last_month_date)+'/NORAD_CAT_ID/'+str(i)+'/orderby/EPOCH asc/format/json/emptyresult/show'
    
    # Getting data in a DataFrame
    df = pd.read_json(session.get(st_query).text)
    
    # Cleaning up the EPOCH column, making sure correct time format is stored
    df['EPOCH'] = df['EPOCH'].replace(r'T',' ', regex=True)
    df['EPOCH'] = pd.to_datetime(df['EPOCH'])
    
    # Adding the DataFrame to the list
    df_list.append(df)
    
    # Getting just the things needed to plot
    df_to_plot_m.append(df)
    
    condition = df['EPOCH'] > last_week_date
    df_to_plot_w.append(df[condition].copy())

    # Saving the Object Name to a list, for easier future use
    list_objects.append(df.loc[df.index[-1],'OBJECT_NAME'])

# Plot the monthly graphs
for df in df_to_plot_m:
    ax = plt.gca()
    df.plot(x='EPOCH', y='APOAPSIS', color = 'blue', linewidth=0.5, ax = ax)
    df.plot(x='EPOCH', y='PERIAPSIS', color = 'green', linewidth=0.5, ax = ax)
    plt.legend(["Apogee", "Perigee"])
    plt.xlabel('Epoch')
    plt.ylabel('Altitude (km)')
    plt.suptitle(str(df.loc[df.index[-1],'OBJECT_NAME'])+" ("+str(df.loc[df.index[-1],'NORAD_CAT_ID'])+")", fontweight='bold')
    plt.title('Last epoch: ' + str(df['EPOCH'].iloc[-1]).partition('.')[0] + ' UTC')
    plt.savefig(str(df.loc[df.index[-1],'NORAD_CAT_ID'])+'-'+'m'+'.png', dpi=300)
    plt.clf()

# Plot the weekly graphs
for df in df_to_plot_w:
    ax = plt.gca()
    df.plot(x='EPOCH', y='APOAPSIS', color = 'blue', linewidth=0.5, ax = ax)
    df.plot(x='EPOCH', y='PERIAPSIS', color = 'green', linewidth=0.5, ax = ax)
    plt.legend(["Apogee", "Perigee"])
    plt.xlabel('Epoch')
    plt.ylabel('Altitude (km)')
    plt.suptitle(str(df.loc[df.index[-1],'OBJECT_NAME'])+" ("+str(df.loc[df.index[-1],'NORAD_CAT_ID'])+")", fontweight='bold')
    plt.title('Last epoch: ' + str(df['EPOCH'].iloc[-1]).partition('.')[0] + ' UTC')
    plt.savefig(str(df.loc[df.index[-1],'NORAD_CAT_ID'])+'-'+'w'+'.png', dpi=300)
    plt.clf()
