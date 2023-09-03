#!/usr/bin/env python3

import sys
import os.path
import csv
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil.parser import parse as parsedate
from dateutil.relativedelta import relativedelta

# using sessions, to remain logged-in to space-track.org, once connected
session = requests.Session()

# bump in the future, as more features are added
ver = "0.4"

# a few predefined time intervals
def days_since(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    today = datetime.now()
    delta = today - date
    return delta.days

def days_between(date_str1, date_str2):
    date1 = datetime.strptime(date_str1, "%Y-%m-%d")
    date2 = datetime.strptime(date_str2, "%Y-%m-%d")
    delta = date1 - date2
    return delta.days

def difference_in_hours(date1):
    d1 = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.now()
    diff = d2 - d1
    return int(diff.total_seconds() / 3660)

# orbital launch sites
launch_site = {
'AFETR' : 'Air Force Eastern Test Range',
'AFWTR': 'Air Force Western Test Range',
'CAS' : 'Pegasus launched from Canary Islands Air Space',
'ERAS' : 'Pegasus launched from Eastern Range Air Space',
'FRGUI' : 'French Guiana',
'HGSTR' : 'Hamma Guira Space Track Range',
'JSC' : 'Jiuquan Satellite Launch Center',
'KODAK' : 'Kodiak Island, Alaska',
'KSCUT' : 'Kagoshima Space Center',
'KWAJL' : 'Kwajalein',
'KYMTR' : 'Kapustin Yar Missile And Space Complex',
'NSC' : 'Naro Space Center',
'OREN' : 'Orenburg',
'PKMTR' : 'Plesetsk Missile And Space Complex',
'PMRF' : 'Pacific Missile Range Facility',
'RLLC' : 'Rocket Lab Launch Complex',
'SADOL' : 'Submarine Launch from Barents Sea',
'SEAL' : 'Sea Launch',
'SEM' : 'Semnan',
'SMTS' : 'Sharud Missile Test Site',
'SNMLP' : 'San Marco Launch Platform',
'SRI' : 'Sirharikota',
'SVOB' : 'Svobodny',
'SWAS' : 'Spaceport Cornwall Air Space',
'TNSTA' : 'Tanegashima Space Center',
'TSC' : 'Taiyaun Space Center',
'TTMTR' : 'Baikonur Cosmodrome',
'UNKN' : 'Unknown',
'VOSTO' : 'Vostochny Cosmodrome',
'VOWAS' : 'Virgin Orbit Western Air Space',
'WLPIS' : 'Wallops Island',
'WOMRA' : 'Woomera',
'WRAS' : 'Pegasus launched from Western Range Air Space',
'WSC' : 'Wenchang Satellite Launch Center',
'XSC' : 'Xichang Space Center',
'YAVNE' : 'Yavne',
'YSLA' : 'Yellow Sea Launch Area',
'YUN' : 'Yunsong',
}

# dictionary for launch sites and countries
launch_country = {
'AFETR' : 'USA',
'AFWTR': 'USA',
'CAS' : 'USA',
'ERAS' : 'USA',
'FRGUI' : 'Europe',
'HGSTR' : 'Europe',
'JSC' : 'China',
'KODAK' : 'USA',
'KSCUT' : 'Japan',
'KWAJL' : 'USA',
'KYMTR' : 'USSR/Russia',
'NSC' : 'South Korea',
'OREN' : 'USSR/Russia',
'PKMTR' : 'USSR/Russia',
'PMRF' : 'USA',
'RLLC' : 'USA',
'SADOL' : 'USSR/Russia',
'SEAL' : 'Sea Launch',
'SEM' : 'Iran',
'SMTS' : 'Iran',
'SNMLP' : 'USA',
'SRI' : 'India',
'SVOB' : 'USSR/Russia',
'SWAS' : 'UK',
'TNSTA' : 'Japan',
'TSC' : 'China',
'TTMTR' : 'USSR/Russia',
'UNKN' : 'Unknown',
'VOSTO' : 'Russia',
'VOWAS' : 'USA',
'WLPIS' : 'USA',
'WOMRA' : 'UK',
'WRAS' : 'USA',
'WSC' : 'China',
'XSC' : 'China',
'YAVNE' : 'Israel',
'YSLA' : 'China',
'YUN' : 'North Korea',
}

# connection to space-track.org
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

# searching in local file for NORAD ID, based on satellite name
def search_satcat(searchstring):
	df = pd.read_csv('satcat.csv')
	match = df['SATNAME'].str.contains(searchstring, case=False)
	results = df.loc[match, ['NORAD_CAT_ID', 'SATNAME', 'LAUNCH', 'DECAY']].reset_index(drop=True)
	results_list = results.values.tolist()
	if len(results_list) == 1:
		return results_list[0][0]
	if len(results_list) >1:
		print(results.to_string(index=False))
		return input('Select desired NORAD_CAT_ID: ')
	if len(results_list) < 1:
		print('No results found!')
		quit()

# establishing the connection to space-tarck.org
connect_to_st()

# updating the local satcat file, along with launch database (for rocket info)
def update_satcat():
	url_satcat = 'https://www.space-track.org/basicspacedata/query/class/satcat/CURRENT/Y/orderby/LAUNCH asc/emptyresult/show'
	df_satcat = pd.read_json(session.get(url_satcat).text)
	df_satcat.to_csv('satcat.csv')
	url_gcat = "https://planet4589.org/space/gcat/tsv/launch/launch.tsv"
	open("launch.tsv", "wb").write(requests.get(url_gcat).content)
	quit()

# get rocket that launched a certain satellite
def get_rocket(object_id):
	with open('launch.tsv', 'r') as file:
		reader = csv.reader(file, delimiter='\t')
		launch_data = [row for row in reader]
	file.close()
	for j in range(0, len(launch_data)):
		if  launch_data[j][0].strip() in object_id:
			return str(launch_data[j][3].strip())

# handle command line arguments:
# if argument is and integer number, that would be NORAD ID
# -n also does the same thing
# -s searches for a satellite in local database
# -u updates the local files
if len(sys.argv) > 1:
    try:
        int(sys.argv[1])
        norad_cat = sys.argv[1]
    except ValueError:
        if sys.argv[1] == '-n': norad_cat = sys.argv[2]
        if sys.argv[1] == '-s': norad_cat = search_satcat(sys.argv[2])
        if sys.argv[1] == '-u': update_satcat()
else:
    print("No command line argument provided.")
    quit()

# getting the GP data in JSON format and creating a DataFrame
url_gp_query = 'https://www.space-track.org/basicspacedata/query/class/gp/NORAD_CAT_ID/'+str(norad_cat)+'/orderby/EPOCH asc/format/json/emptyresult/show'
df_gp = pd.read_json(session.get(url_gp_query).text)

# if GP data is valid, define a few variables and display the data
if len(df_gp) > 0:
	df_gp['EPOCH'] = df_gp['EPOCH'].replace(r'T',' ', regex=True)
	df_gp['EPOCH'] = pd.to_datetime(df_gp['EPOCH'])
	OBJECT_NAME = str(df_gp.iloc[0]['OBJECT_NAME'])
	OBJECT_ID = str(df_gp.iloc[0]['OBJECT_ID'])
	ROCKET = get_rocket(OBJECT_ID)
	NORAD_CAT_ID = str(df_gp.iloc[0]['NORAD_CAT_ID'])
	EPOCH = str(df_gp.iloc[0]['EPOCH']).split('.')[0]
	PERIOD = str(df_gp.iloc[0]['PERIOD'])
	INCLINATION = str(df_gp.iloc[0]['INCLINATION'])
	APOAPSIS = str(df_gp.iloc[0]['APOAPSIS'])
	PERIAPSIS = str(df_gp.iloc[0]['PERIAPSIS'])
	OBJECT_TYPE = str(df_gp.iloc[0]['OBJECT_TYPE'])
	RCS_SIZE = str(df_gp.iloc[0]['RCS_SIZE'])
	if RCS_SIZE == "SMALL": RCS_SIZE = "SMALL (<0.1m2)"
	if RCS_SIZE  == "MEDIUM": RCS_SIZE = "MEDIUM (0.1m2 - 1m2)"
	if RCS_SIZE  == "LARGE": RCS_SIZE = "LARGE (>1m2)"
	SITE = str(df_gp.iloc[0]['SITE'])
	DECAY = str(df_gp.iloc[0]['DECAY_DATE'])
	LAUNCH_DATE = str(df_gp.iloc[0]['LAUNCH_DATE'])
	COMMENT = str(df_gp.iloc[0]['COMMENT'])
	days_in_orbit = days_since(LAUNCH_DATE)
	print("==========================================================")
	print("Data for: "+OBJECT_NAME)
	print("==========================================================")
	if EPOCH == "nan": 
		print ("oops")
		quit()
	print("Epoch: "+EPOCH+' UTC, '+str(difference_in_hours(str(EPOCH)))+" hours ago")
	print("NORAD ID:   "+NORAD_CAT_ID)
	print("Designator: "+OBJECT_ID)
	print("Size: "+RCS_SIZE)
	print("Type: "+OBJECT_TYPE)
	print("Launch date: "+LAUNCH_DATE)
	print("Launch site: "+launch_site[SITE])
	# Maybe the launch.tsv file isn't updated yet, in that case, don't display rocket name
	if ROCKET is not None: print("Rocket: "+ROCKET)
	print("Country: "+launch_country[SITE])
	if DECAY == "nan":
		print("Days in orbit: ",days_in_orbit,"(ongoing)")
	else:
		print("Reentry date:  ",DECAY)
		print("Days in orbit: ",days_between(DECAY, LAUNCH_DATE))
	print("---------------------------------------------------------")
	print("Inclin.: ", INCLINATION, "degrees")
	print("Period:  ", PERIOD, "minutes")
	print("Perigee: ", PERIAPSIS, "km")
	print("Apogee:  ", APOAPSIS, "km")
	print("---------------------------------------------------------")
	print("Done!                   OMMData v"+ver+" by claudiu@parsec.ro")
	print()
	choice = input("Insert plot parameters, or 0 to exit: ")
	if choice == "0": quit()

	# starting point for time interval can be provided as in format:
	# '2020-12-31' or partial, like '2020' or '2020-12'
	plot_start_date = choice

	now = datetime.now()
	last_month_date = now + relativedelta(months=-1)
	last_month_date = str(last_month_date).split(" ")[0]
	last_week_date = now + relativedelta(weeks=-1)
	last_week_date = str(last_week_date).split(" ")[0]

	# defining alternatives for the plot time interval:
	# 'l' --since launch
	# 'm' --last month
	# 'w' --last week
	if 'l' in choice: plot_start_date = LAUNCH_DATE
	if 'w' in choice: plot_start_date = last_week_date
	if 'm' in choice: plot_start_date = last_month_date

	# increasing the plot size
	plot_width  = 12.8
	plot_height =  9.6

	# is 's' is used, the resulted plot will be smaller
	if 's' in choice:
		plot_width  = 6.4
		plot_height = 4.8

	# fetching data needed for plotting
	plot_query = 'https://www.space-track.org/basicspacedata/query/class/gp_history/EPOCH/>'+str(plot_start_date)+'/NORAD_CAT_ID/'+NORAD_CAT_ID+'/orderby/EPOCH asc/format/json/emptyresult/show'
	df_plot = pd.read_json(session.get(plot_query).text)
	
	# adjusting time format in DataFrame
	df_plot['EPOCH'] = df_plot['EPOCH'].replace(r'T',' ', regex=True)
	df_plot['EPOCH'] = pd.to_datetime(df_plot['EPOCH'])


	fig = plt.figure(figsize=(plot_width, plot_height))
	ax = plt.gca()
	df_plot.plot(x='EPOCH', y='APOAPSIS', color = 'blue', linewidth=0.5, ax = ax)
	df_plot.plot(x='EPOCH', y='PERIAPSIS', color = 'green', linewidth=0.5, ax = ax)
	plt.legend(["Apogee", "Perigee"])
	plt.xlabel('Epoch')
	plt.ylabel('Altitude (km)')
	plt.suptitle(OBJECT_NAME+" ("+NORAD_CAT_ID+")", fontweight='bold')
	plt.title('Last epoch: ' + EPOCH.partition('.')[0] + ' UTC')
	plt.show()
	plt.clf()

# if the object is not in LEO anymore, handle the situation by using SATCAT to provide some data
# no plot in this case
else:
	url_omm_query = 'https://www.space-track.org/basicspacedata/query/class/satcat/NORAD_CAT_ID/'+str(norad_cat)+'/orderby/LAUNCH asc/format/xml/emptyresult/show'
	df_satcat = pd.read_xml(session.get(url_omm_query).text)
	OBJECT_NAME = str(df_satcat.iloc[0]['OBJECT_NAME'])
	OBJECT_TYPE = str(df_satcat.iloc[0]['OBJECT_TYPE'])
	OBJECT_ID = str(df_satcat.iloc[0]['INTLDES'])
	ROCKET = get_rocket(OBJECT_ID)
	NORAD_CAT_ID = str(df_satcat.iloc[0]['NORAD_CAT_ID'])
	LAUNCH_DATE = str(df_satcat.iloc[0]['LAUNCH'])
	SITE = str(df_satcat.iloc[0]['SITE'])
	COMMENT = str(df_satcat.iloc[0]['COMMENT'])
	ROCKET = get_rocket(OBJECT_ID)
	print("==========================================================")
	print("Data for: "+OBJECT_NAME)
	print("==========================================================")
	print("NORAD ID:   "+NORAD_CAT_ID)
	print("Designator: "+OBJECT_ID)
	print("Type: "+OBJECT_TYPE)
	print("Launch date: "+LAUNCH_DATE)
	print("Launch site: "+launch_site[SITE])
	print("Rocket: "+ROCKET)
	print("Country: "+launch_country[SITE])
	print(COMMENT)
	print("---------------------------------------------------------")
	print("Done!                   OMMData v"+ver+" by claudiu@parsec.ro")
	print()
	quit()
