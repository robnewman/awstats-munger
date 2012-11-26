from django.contrib import admin
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch.dispatcher import receiver
from django.utils.log import logger

class SourceFile(models.Model):
    """
    Represents an awstats or other file with data.  This stores the last time
    the file was read, so changes can be intelligently handled.
    """
    filename = models.CharField(max_length=100, blank=False, editable=False)
    last_read = models.DateTimeField()

    class Meta:
        ordering = ['-last_read']

class Month(models.Model):
    """
    Month-level data.  This isn't always the same as an aggregation
    of days -- for example, unique_visitor counts across the whole month.
    """
    source_file = models.ForeignKey(SourceFile, blank=False, null=False, editable=False)
    date = models.DateField(blank=False, editable=False, unique=True)
    visits = models.IntegerField()
    unique_visitors = models.IntegerField()

    def __str__(self):
        return "{0}: {1}".format(self.date, self.visits)

    class Meta:
        ordering = ['-date']

class Day(models.Model):
    """
    Day-level data.
    """
    source_file = models.ForeignKey(SourceFile, blank=False, null=False, editable=False)
    date = models.DateField(blank=False, editable=False, unique=True)
    pages = models.IntegerField()
    views = models.IntegerField()
    bandwidth = models.IntegerField()
    visits = models.IntegerField()

    def __str__(self):
        return "{0}: {1}".format(self.date, self.views)

    class Meta:
        ordering = ['-date']
