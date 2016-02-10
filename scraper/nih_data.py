#!/user/bin/env python3

'''Download NIH RePORTER database and find project data for funded researchers.'''

from __future__ import unicode_literals
import shutil
import re
import zipfile
import csv
import locale
import os.path
import urllib2
from scraper.models import Author, Project

_BASE_SUMMARY_URL = "https://projectreporter.nih.gov/project_info_description.cfm?aid={app_id}"
_BASE_DATA_FILENAME = "RePORTER_PRJ_C_FY{year}.{extension}"
# Choose between CSV and XML
_BASE_DATA_URL = "http://exporter.nih.gov/CSVs/final/RePORTER_PRJ_C_FY{year}.zip"
# _BASE_DATA_URL = "http://exporter.nih.gov/XMLData/final/RePORTER_PRJ_X_FY{year}.zip"

_APP_ID_IDX = 0
_PI_IDX = 29
_PROJ_TITLE_IDX = 34
_TOTAL_COST_IDX = 43
_SUB_COST_IDX = 44


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # from https://docs.python.org/2/library/csv.html
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]


def encoder(unicode_csv_data):
    # from https://docs.python.org/2/library/csv.html
    for line in unicode_csv_data:
        try:
            yield line.encode('utf-8').rstrip()
        except UnicodeDecodeError:
            continue


def get_query_regex(name):
    ''' Generates a query regex of the form \bNAME\b
    Name is assumed to be of the form Lastname, Firstname MI.'''
    return r"\b" + name.upper() + r"\b"


def _require_csv_file(fiscal_year, force_redownload=False, force_reunzip=False):
    '''Download the CSV file for the passed fiscal year if necessary.
    Return True if successful, False otherwise.
    '''
    csv_filename = _BASE_DATA_FILENAME.format(year=fiscal_year, extension='csv')
    zip_filename = _BASE_DATA_FILENAME.format(year=fiscal_year, extension='zip')
    csv_file_exists = os.path.isfile(csv_filename)
    zip_file_exists = os.path.isfile(zip_filename)

    if csv_file_exists and not force_redownload and not force_reunzip:
        print "File already exists:", csv_filename
        return True

    # Download zip file
    if not zip_file_exists or force_redownload:
        url = _BASE_DATA_URL.format(year=fiscal_year)
        print "Downloading from {}...".format(url)
        request = urllib2.urlopen(url)
        with open(zip_filename, 'wb') as zip_file:
            shutil.copyfileobj(request, zip_file)

    return os.path.isfile(zip_filename)


def _total_cost(csv_entry):
    '''Get the total cost for a project.
    Takes the max of the 'total cost' and 'sub cost' fields--sometimes
    'total cost' is left blank and its value is placed in the
    'sub cost' field.
    '''
    total_cost = csv_entry[_TOTAL_COST_IDX]
    sub_cost = csv_entry[_SUB_COST_IDX]
    if total_cost == '':
        total_cost = '0'
    if sub_cost == '':
        sub_cost = '0'
    total_cost = int(total_cost)
    sub_cost = int(sub_cost)
    total_cost = max(sub_cost, total_cost)
    return total_cost


def save_projects_data(researcher, year):
    '''Get project data for projects associated with passed
    researcher in passed filename.
    '''
    zip_filename = _BASE_DATA_FILENAME.format(year=year, extension='zip')
    csv_filename = _BASE_DATA_FILENAME.format(year=year, extension='csv')
    with zipfile.ZipFile(open(zip_filename, 'r')) as zip_file:
        with zip_file.open(csv_filename, 'r') as csv_file:
            data_reader = unicode_csv_reader(csv_file, quotechar=str('"'))
            for entry in data_reader:
                if len(entry) < 45:
                    continue

                principal_investigators = entry[_PI_IDX]
                pi_participated_in_entry = re.search(
                    get_query_regex(researcher.name),
                    principal_investigators) is not None

                if not pi_participated_in_entry:
                    continue

                title = entry[_PROJ_TITLE_IDX]
                total_cost = _total_cost(entry)
                app_id = entry[_APP_ID_IDX]
                url = _BASE_SUMMARY_URL.format(app_id=app_id)
                print '-' * 10
                print "Researcher:", researcher.name
                print "Project:", title
                print "URL:", url
                funding_str = locale.currency(total_cost, grouping=True)[:-3]
                print("Amount:", funding_str)
                query = Project.objects.filter(title=title, year=int(year))
                if not query:
                    # only create the project if it doesn't exist yet
                    project = Project(
                        researcher=researcher,
                        title=title,
                        url=url,
                        funding_amount=total_cost,
                        year=int(year))
                else:
                    project = query[0]
                    project.funding_amount = total_cost
                project.save()


def scrape(year):
    # needed for currency
    locale.setlocale(locale.LC_ALL, '')

    _require_csv_file(year)

    for researcher in Author.objects.all():
        save_projects_data(researcher, year)
