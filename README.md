awstats-munger
==============

Python scripts to munge awstats flat files and output in CSV and possibly 
into Django MTV

Usage
=====
    python process.py -v awstats.hostname.txt WebStats.csv
    2012-11-26 14:43:30 File in: 'awstats.hostname.txt', file out: 'WebStats.csv'
    2012-11-26 14:43:30 Datetime obj: 2012-11-15 00:00:00
    2012-11-26 14:43:30 Pages: 258861, All visits: 44899, Uniq. visitors: 33015
    2012-11-26 14:43:30 Appending to CSV...
    2012-11-26 14:43:31 Date '2012-11-15' already in file 'data/WebStats.csv'. Ignoring...

Notes
=====
* Initial importer.py and models.py created by Adam Clark.

Links
=====
* http://awstats.sourceforge.net/
