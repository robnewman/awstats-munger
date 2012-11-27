awstats-munger
==============

Python scripts to munge awstats flat files and output in CSV and
possibly into Django MTV (future plans).

The command line process.py script expects awstats to be in [day format](http://www.internetofficer.com/awstats/daily-stats/).

CSV output is designed for easy integration with DyGraphs.

Prerequisites
=============

You must create your AWstats database files on a day-by-day basis
instead of monthly in order to get the unique-visitor statistic.
This statistic is not currently available in the default monthly
view.

Below is an example of how you would do this:

    perl /path/to/awstats.pl -config=hostname -update -databasebreak=day
    Create/Update database for config "/path/to/awstats.hostname.conf" by AWStats...
    From data in log file...
    Phase 1 : First bypass old records, searching new record...
    Searching new records from beginning of log file...

Usage
=====
    %> python process.py -v awstats.hostname.txt WebStats.csv
    2012-11-26 14:43:30 File in: 'awstats.hostname.txt', file out: 'WebStats.csv'
    2012-11-26 14:43:30 Datetime obj: 2012-11-15 00:00:00
    2012-11-26 14:43:30 Pages: 258861, All visits: 44899, Uniq. visitors: 33015
    2012-11-26 14:43:30 Appending to CSV...
    2012-11-26 14:43:31 Date '2012-11-15' already in file 'data/WebStats.csv'. Ignoring...

Output
======

Output is in a CSV text file in the format:

    date,total visitors,unique visitors
    2004-12-01,6271,6000
    2004-12-02,6327,6000
    2004-12-03,5514,5000
    2004-12-04,4480,4000
    2004-12-05,5699,5000
    2004-12-06,6957,6000
    ....
    2012-11-02,32958,30000
    2012-11-03,30458,30000
    2012-11-04,33623,30000
    2012-11-05,36335,30000
    2012-11-06,36170,30000
    2012-11-07,57518,50000
    2012-11-08,49356,40000

Notes
=====
* Initial importer.py and models.py created by Adam Clark.
* Directory you write to must have permissions that allow writing.

Links
=====
* [AWStats](http://awstats.sourceforge.net/)
* [DyGraphs](http://dygraphs.com/)
