from importer import AWStatsReader, CSVReader
from time import strftime
from datetime import datetime
from optparse import OptionParser

"""
Script to read AWStats and write out data
to CSV file
"""

def logfmt(message):
    """
    Out a log message
    with a timestamp
    """
    print strftime("%Y-%m-%d %H:%M:%S"), message

def usage():
    """
    Read options
    """
    usage = "Usage: %prog [options] awstats_in outfile.csv"
    epilog = ["Note: Awstats data ",
              "file must be in day format "
              "as it is the only format with "
              "unique visitors"]
    parser = OptionParser(usage=usage, epilog=" ".join(epilog))
    parser.add_option('-v',
                      action="store_true",
                      dest="verbose",
                      help="verbose output",
                      default=False)
    (options, args) = parser.parse_args()

    if options.verbose:
        verbose = True
    else:
        verbose = False

    if len(args) > 1:
        file_in = args[0]
        file_out = args[1]
    else:
        file_in = args[0]
        file_out = args[1]

    return file_in, file_out, verbose

def main():
    """
    Process the log file
    and dump to CSV
    """
    file_in, file_out, verbosity = usage()
    if verbosity:
        logfmt("File in: '%s', file out: '%s'" % (file_in, file_out))

    reader = AWStatsReader(file_in)
    day_data = reader.read_section(AWStatsReader.DAY_MARKER)
    single_date_str = day_data.popitem()

    datetime_obj = datetime.strptime(single_date_str[0], '%Y%m%d')
    datetime_str = datetime.strftime(datetime_obj, '%Y-%m-%d')
    pages, views, bandwidth, visits = single_date_str[1]
    day_stats = reader.read_section(AWStatsReader.MONTH_MARKER)
    total_visitors = day_stats['TotalVisits'][0]
    unique_visitors = day_stats['TotalUnique'][0]

    if verbosity:
        logfmt("Datetime obj: %s" % datetime_obj)
        logfmt("Pages: %s, All visits: %s, Uniq. visitors: %s" % (pages,
                                                                  total_visitors,
                                                                  unique_visitors))
        logfmt("Appending to CSV...")

    csv = CSVReader(file_out)
    entries = csv.read_lines()

    if datetime_str not in list(entries.keys()):
        if verbosity:
            logfmt("Date '%s' not found, appending..." % datetime_str)
        entries[datetime_str] = [total_visitors, unique_visitors]
        try:
            csv.write_entries(entries)
        except Exception, e:
            print "Caught exception %s" % e
        else:
            if verbosity:
                logfmt("Done!")
    else:
        if verbosity:
            logfmt("Date '%s' already in file '%s'. Ignoring..." % (datetime_str, file_out))

if __name__ == '__main__':
    main()
