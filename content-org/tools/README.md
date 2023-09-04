# ommdata
Python script for fetching orbital data from Space-Track.org

## Features

- displays concise information of _any_ orbital object tracked by Space-Track.org;
- displays some data also for decayed objects;
- plots apogee and perigee information for any object, decayed or active, on any time interval;
- if NORAD-ID is not known, the user can search for it, in a local database;
- requests to Space-Track.org are minimal;
- avoided third-party data sources and dependinces (with the exception of launcher data, fetched from [GCAT](https://planet4589.org/space/gcat/)).

## Prerequisites

- Python3;
- space-track.org login data needed (create a file called 'secrets.txt' with your username on one line and your password on the second line).

## Usage

- 'python3 ommdata.py -u' --updates the local files, or on first run, will fetch the files from space-track and GCAT; recommending using this option on first run, since the mentioned files are not distributed here and it will not work without them;
- 'python3 ommdata.py NNNNN' (or -n NNNNN) --will consider NNNNN a valid NORAD-ID and display data on the object; NNNNN must be an integer number;
- 'python3 ommdata.py -s explorer' --will search for all satellites named 'explorer' and display a list to choose a NORAD-ID from; if there's only one match, the NORAD-ID is selected automatically;
- after the data is displayed and if the object is/was in LEO, there's an option to plot a apogee/perigee graph for the seelcted object; starting point for time interval can be provided as in format: '2020-12-31' or partial, like '2020' or '2020-12' or you can provide 'l' --since launch, 'm' --last month or 'w' --last week.

## Other files

- gen_img.py --for generating weekly and monthly plots for any number of objects;
- conj.py --playing with usign GP data to identify close approaches between two orbital objects.

## Sources
- [Space-Track.org](www.space-track.org) for most data;
- [Jonathan MacDowell](https://planet4589.org) for GCAT data;
- [ChatGPT](https://chat.openai.com/chat) for helping me with Python code.
