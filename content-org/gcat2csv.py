#!/usr/bin/env python3

import sys
import datetime
import hashlib
import os.path
import requests
import pandas as pd
from datetime import date
from dateutil.parser import parse as parsedate
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from spacetrack import SpaceTrackClient

list_args = sys.argv

# '-x' --just exit immediately, for testing purposes
# '-l' --local build, doesn't fetch new GCAT files, doesn't handle github changes
# '-c' --placeholder, if no argument is passed, normal run of the script, only used to avoid errors

if len(list_args) == 1: list_args.append('-c')

if list_args[1] == '-x': 
	print('Bye!')
	exit()

# files needed for initial raw data import from upstream
FILE_PADS = "sites.tsv"
FILE_TEMP2 = "sites.tmp"
FILE_DATA = "launchdata.tsv"
FILE_TEMP = "launchdata.tmp"

# hardcoding countries with orbital launch attempts
country = ["SUA", "Rusia", "China", "Europa", "Japonia", "India", "Iran", "Israel", "Coreea de Sud", "Coreea de Nord", "Brazilia"]

# getting the current year in a variable
today = datetime.now()
curr_year = today.year

def update_GCAT():
	
	if os.path.isfile(FILE_TEMP): os.remove(FILE_TEMP)
	
	print('Checking for GCAT update...')
	url = 'https://planet4589.org/space/gcat/tsv/launch/launch.tsv'
	response = requests.get(url, allow_redirects=True)
	open(FILE_TEMP,"wb").write(response.content)

	r = requests.head(url)
	url_time = r.headers['last-modified']
	url_date = parsedate(url_time)

	md5_hash = hashlib.md5
	with open(FILE_TEMP,"rb") as f:
		bytes = f.read()
		readable_hash = hashlib.md5(bytes).hexdigest()

	if os.path.isfile(FILE_DATA):
		with open(FILE_DATA,"rb") as g:
			bytes = g.read()
			readable_hash2 = hashlib.md5(bytes).hexdigest()
			if readable_hash == readable_hash2: 
				os.remove(FILE_TEMP)
				print ("No update found!")
			else: 
				os.remove(FILE_DATA)
				os.rename(FILE_TEMP,FILE_DATA)
				print ("New GCAT version installed, date:",url_date)
	else:
		os.rename(FILE_TEMP,FILE_DATA)
		print ("No old GCAT found, fetched latest version from date",url_date)
		
def update_PADS():

	if os.path.isfile(FILE_TEMP2): os.remove(FILE_TEMP2)

	url = 'https://planet4589.org/space/gcat/tsv/tables/sites.tsv'
	response = requests.get(url, allow_redirects=True)
	open(FILE_TEMP2,"wb").write(response.content)

	r = requests.head(url)
	url_time = r.headers['last-modified']
	url_date = parsedate(url_time)

	md5_hash = hashlib.md5
	with open(FILE_TEMP2,"rb") as f:
		bytes = f.read()
		readable_hash = hashlib.md5(bytes).hexdigest()

	if os.path.isfile(FILE_PADS):
		with open(FILE_PADS,"rb") as g:
			bytes = g.read()
			readable_hash2 = hashlib.md5(bytes).hexdigest()
			if readable_hash == readable_hash2: 
				os.remove(FILE_TEMP2)
			else: 
				os.remove(FILE_PADS)
				os.rename(FILE_TEMP2,FILE_PADS)
	else:
		os.rename(FILE_TEMP2,FILE_PADS)
		print ("No old PADS found, fetched latest version from date",url_date)

# Download files if they are not present in current directory
#if not os.path.isfile(FILE_DATA): update_GCAT()
#if not os.path.isfile(FILE_PADS): update_PADS()
if list_args[1] != '-l': 
	update_GCAT()
	update_PADS()

print('Processing data...')

# Importing upstream files into dataframes
df = pd.read_csv(FILE_DATA, sep='\t', header=None, skiprows=lambda x: x<2, names=['Launch_Tag', 'Launch_JD', 'Launch_Date', 'LV_Type', 'Variant', 'Flight_ID', 'Flight', 'Mission', 'FlightCode', 'Platform', 'Launch_Site', 'Launch_Pad', 'Ascent_Site', 'Ascent_Pad', 'Apogee', 'Apoflag', 'Range', 'RangeFlag', 'Dest', 'Agency', 'Launch_Code', 'Group', 'Category', 'LTCite', 'Cite', 'Notes'])
pads = pd.read_csv(FILE_PADS, sep='\t', header=None, skiprows=lambda xx: xx<2, names=['Site', 'Code', 'UCode', 'Type', 'StateCode', 'TStart', 'TStop', 'ShortName', 'Name', 'Location', 'Longitude', 'Latitude', 'Error', 'Parent', 'ShortEName', 'EName', 'Group', 'UName'])

# Cleaning up the countries a bit
pads['StateCode'] = pads['StateCode'].replace('DZ','EU', regex=True)
pads['StateCode'] = pads['StateCode'].replace('J','JP', regex=True)
pads['StateCode'] = pads['StateCode'].replace('GUF','EU', regex=True)
pads['StateCode'] = pads['StateCode'].replace('AU','EU', regex=True)
pads['StateCode'] = pads['StateCode'].replace('NZ','US', regex=True)
pads['StateCode'] = pads['StateCode'].replace('TTPI','US', regex=True)
pads['StateCode'] = pads['StateCode'].replace('ESCN','US', regex=True)
pads['StateCode'] = pads['StateCode'].replace('KE','US', regex=True)
pads['StateCode'] = pads['StateCode'].replace('KI','RU', regex=True)
pads['StateCode'] = pads['StateCode'].replace('SU','RU', regex=True)
pads['StateCode'] = pads['StateCode'].replace('UK','US', regex=True)

# Quick and dirty fix, since I consider 2022-U02 to be a proper failed launch deserving the F tag
# To be removed if this changes upstream
df['Launch_Tag'] = df['Launch_Tag'].replace('2020-U01', '2020-F0x', regex=True)
df['Launch_Tag'] = df['Launch_Tag'].replace('2022-U02', '2022-F0x', regex=True)

# Filtering suborbital launches
df = df[df["Launch_Tag"].str.contains("-S") == False]
df = df[df["Launch_Tag"].str.contains("-A") == False]
df = df[df["Launch_Tag"].str.contains("-M") == False]
df = df[df["Launch_Tag"].str.contains("-W") == False]
df = df[df["Launch_Tag"].str.contains("-Y") == False]
df = df[df["Launch_Tag"].str.contains("-U") == False]
df = df[df["Launch_Tag"].str.contains("2014-000") == False]

# Changing date format
df['Launch_Date'] = df['Launch_Date'].replace(' Jan ', '-01-', regex=True)
df['Launch_Date'] = df['Launch_Date'].replace(' Feb ', '-02-', regex=True)
df['Launch_Date'] = df['Launch_Date'].replace(' Mar ', '-03-', regex=True)
df['Launch_Date'] = df['Launch_Date'].replace(' Apr ', '-04-', regex=True)
df['Launch_Date'] = df['Launch_Date'].replace(' May ', '-05-', regex=True)
df['Launch_Date'] = df['Launch_Date'].replace(' Jun ', '-06-', regex=True)
df['Launch_Date'] = df['Launch_Date'].replace(' Jul ', '-07-', regex=True)
df['Launch_Date'] = df['Launch_Date'].replace(' Aug ', '-08-', regex=True)
df['Launch_Date'] = df['Launch_Date'].replace(' Sep ', '-09-', regex=True)
df['Launch_Date'] = df['Launch_Date'].replace(' Oct ', '-10-', regex=True)
df['Launch_Date'] = df['Launch_Date'].replace(' Nov ', '-11-', regex=True)
df['Launch_Date'] = df['Launch_Date'].replace(' Dec ', '-12-', regex=True)
df['Launch_Date'] = df['Launch_Date'].replace('- ', '-0', regex=True)
df['Launch_Date'] = df['Launch_Date'].replace(';', ':', regex=True)

# Changing some rockets' name
#df['LV_Type'] = df['LV_Type'].replace('Delta 4H', 'Delta IV Heavy', regex=True)
df['LV_Type'] = df['LV_Type'].replace('Soyuz-2-1A', 'Soyuz-2.1a', regex=True)
df['LV_Type'] = df['LV_Type'].replace('Soyuz-2-1B', 'Soyuz-2.1b', regex=True)
df['LV_Type'] = df['LV_Type'].replace('Soyuz-2-1V', 'Soyuz-2.1v', regex=True)
#df['LV_Type'] = df['LV_Type'].replace('GSLV Mk II', 'GSLV Mk. 2', regex=True)
df['LV_Type'] = df['LV_Type'].replace('GSLV Mk III', 'LVM3', regex=True)

# Removing seconds from timestamps
df['Launch_Date'] = df['Launch_Date'].apply(lambda x: x.split(':')[0] if len(x) > 16 else x)

# Adding the 'Country' column, based on launch pads country code in sites.tsv
dict_Site = dict(zip(pads.Site, pads.StateCode))
df['Country'] = df['Launch_Site'].map(dict_Site)

# adding 'Outcome' column, based on Launch_Tag
df['Outcome'] = df['Launch_Tag'].map(lambda x: 'F' if 'F' in x else 'S')

def merge_missions(val1, val2):
    if val2.strip() in ['', '-', val1]:
        return val1
    else:
        return f"{val1} ({val2})"

def merge_pads(val1, val2):
    if val2.strip() in ['', '-']:
        return val1
    else:
        return f"{val1} {val2}"

df['Mission'] = df.apply(lambda row: merge_missions(row['Flight'], row['Mission']), axis=1)
df['Launch_Site'] = df.apply(lambda row: merge_pads(row['Launch_Site'], row['Launch_Pad']), axis=1)

# Export the reformatted file as CSV, while filtering out some columns
print("Exporting data...")
df[['Launch_Tag','Launch_JD','Launch_Date','LV_Type','Variant','Flight_ID', 'Mission','Platform','Launch_Site','Agency','Launch_Code', 'Category', 'Country','Outcome']].to_csv('data.csv', index=False)
print("Done!")