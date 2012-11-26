from WebsiteStats import settings
from WebsiteStats.stats.models import SourceFile, Quake, Day, Month
from datetime import date, datetime, time
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import deserialize
from django.db.models.aggregates import Max
from django.utils.log import logger
from genericpath import isfile, isdir
from glob import glob
from urlparse import urljoin
import json
import math
import os.path
import re
import string
import urllib2


STATFILE_GLOB = 'data/awstats*.txt'

class AWStatsReader(object):
    """
    Object that wraps around an awstats data file and provides
    a simple query API to pull data from various sections.

    This generally operates off the assumption that each line of data is a
    space-delimited list of elements, where the first element is a unique
    identifier.  For example, each line of day data looks like
    # Day     pages  views  bandwidth  visits
    20110301 251892 481993 68914212105 40664

    Example:
    > reader = AWStatsReader("awstats.txt")
    > day_data = reader.read_section(AWStatsReader.DAY_MARKER)
    > day_data['20110301']
    ['251892', '481993', '68914212105', '40664']
    """

    file = None
    sections = None

    MAP_SECTION = "MAP"
    BEGIN_MARKER = "BEGIN_{0}"
    END_MARKER = "END_{0}"
    POS_MARKER = "POS_{0}"

    DAY_MARKER = "DAY"
    MONTH_MARKER = "GENERAL"
    PATHS_MARKER = "SIDER"

    def __init__(self, filename):
        self.file = open(filename)

    def close(self):
        self.file.close()

    def validate_begin(self, section):
        line = self.file.readline()
        (label, count) = line.rstrip().split()
        expected_marker = self.BEGIN_MARKER.format(section)
        if label != expected_marker:
            raise Exception("Found {0} but expected {1}".format(label,
                                                                expected_marker))
        return int(count)

    def read_lines(self, num_lines):
        data = {}
        for line in [self.file.readline().rstrip() for _x in range(num_lines)]:
            fields = line.split()
            data[fields[0]] = fields[1:]
        return data

    def validate_end(self, section):
        label = self.file.readline().rstrip()
        expected_marker = self.END_MARKER.format(section)
        if label != expected_marker:
            raise Exception("Found {0} but expected {1}".format(label,
                                                                expected_marker))

    def read_map(self):
        self.file.seek(0)
        max_lines_to_map = 50
        count = None
        for _x in range(max_lines_to_map):
            try:
                count = self.validate_begin(self.MAP_SECTION)
            except Exception:
                pass
            if count is not None:
                break
        if count is None:
            raise Exception("Failed to find the mapping block")
        section_data = self.read_lines(count)
        self.validate_end(self.MAP_SECTION)
        self.sections = dict([ (k,int(v[0])) for (k,v) in section_data.iteritems() ])

    def read_section(self, section):
        if self.sections is None:
            self.read_map()
        offset = self.sections[self.POS_MARKER.format(section)]
        self.file.seek(offset)
        num_lines = self.validate_begin(section)
        data = self.read_lines(num_lines)
        self.validate_end(section)
        return data

class AWStatsCollector(object):
    """
    Class to pull awstats data into the data models.  It ties each file to
    a SourceFile object, so it won't operate unless the file has changed since
    the last visit.

    The intent is to be able to run a cron job like
    > collector = AWStatsCollector()
    > collector.read_files()
    """

    def read_file(self, filename):
        now = datetime.today()

        logger.info("Looking at {0}".format(filename))

        try:
            source_file = SourceFile.objects.get(filename=filename)
            source_file.last_read = now
        except ObjectDoesNotExist:
            source_file = SourceFile(filename=filename, last_read=now)

        reader = AWStatsReader(filename)

        try:
            day_data = reader.read_section(AWStatsReader.DAY_MARKER)
            # path_data = reader.read_section(AWStatsReader.PATHS_MARKER)
            for (day_str, data) in day_data.iteritems():
                try:
                    day_date = datetime.strptime(day_str, "%Y%m%d")
                    (pages, views, bandwidth, visits) = [int(v) for v in data]
                    try:
                        day = Day.objects.get(date=day_date)
                    except ObjectDoesNotExist:
                        day = Day(date=day_date, source_file=source_file)
                    day.pages=pages
                    day.views=views
                    day.bandwidth=bandwidth
                    day.visits=visits
                    day.save()
                except Exception as e:
                    logger.error("Failed to parse day data from {0} / {1} : {2}".format(day_str, data, e))

            month_data = reader.read_section(AWStatsReader.MONTH_MARKER)
            try:
                month = Month.objects.get(source_file_id=source_file.id)
            except ObjectDoesNotExist:
                month_fields = re.search(r'(\d\d)(\d\d\d\d)', filename)
                if not month_fields:
                    raise Exception("Couldn't get month from filename ".format(filename))
                month_date = datetime(int(month_fields.group(2)), int(month_fields.group(1)), 1) 
                month = Month(source_file=source_file, date=month_date)
            month.visits = month_data['TotalVisits']
            month.unique_visitors = month_data['TotalUnique']
            month.save()

            source_file.save()
        finally:
            reader.close()

    def read_files(self):
        last_updated = SourceFile.objects.aggregate(Max('last_read')).values()[0]
        logger.info("Last updated = {0}".format(last_updated))

        filenames = glob(os.path.join(settings.AWSTATS_PATH, STATFILE_GLOB))
        for filename in filenames:
            mtime = datetime.fromtimestamp(os.path.getmtime(filename))
            if last_updated is None or mtime > last_updated:
                logger.info("Updating from {0}".format(filename))
                self.read_file(filename)
            else:
                logger.info("No updates for {0}".format(filename))
