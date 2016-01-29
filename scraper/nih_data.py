#!/user/bin/env python3

'''Download NIH RePORTER database and find project data for funded researchers.'''

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


def get_query_regex(name):
    ''' Generates a query regex of the form \bNAME\b
    Name is assumed to be of the form Lastname, Firstname MI.'''
    return r"\b" + name.upper() + r"\b"


def _decode_file(filename):
    '''Remove carriage returns from passed filename.
    Creates a temporary file, reads it as a bytes stream, then
    writes back as a text file.
    '''
    tmp_filename = 'tmp'
    shutil.copyfile(filename, tmp_filename)
    with open(tmp_filename, 'rb') as unfixed:
        with open(filename, 'w') as fixed:
            # print "Failed lines:", "-" * 10, "\n\n"
            for line in unfixed:
                fixed_line = line.rstrip()
                if len(fixed_line) == 0:
                    continue
                try:
                    fixed_line = fixed_line.decode('utf-8')
                    fixed.write(fixed_line)
                    fixed.write('\n')
                except UnicodeDecodeError:
                    # print '\n', fixed_line
                    pass
            # print "\n\n/Failed lines", "-" * 10
    os.remove(tmp_filename)


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

    # Unzip data file
    if not csv_file_exists or force_reunzip:
        print "Unzipping {}...".format(zip_filename)
        zip_ref = zipfile.ZipFile(zip_filename, 'r')
        zip_ref.extractall()
        _decode_file(csv_filename)

    return os.path.isfile(csv_filename)


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


def save_projects_data(researcher, filename, year):
    '''Get project data for projects associated with passed
    researcher in passed filename.
    '''
    with open(filename, 'r') as csv_file:
        data_reader = csv.reader(csv_file, quotechar='"')
        for entry in data_reader:
            if len(entry) < 45:
                continue

            principal_investigators = entry[_PI_IDX]
            pi_participated_in_entry = re.search(
                get_query_regex(researcher.name), principal_investigators) is not None

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
    csv_filename = _BASE_DATA_FILENAME.format(year=year, extension='csv')

    for researcher in Author.objects.all():
        save_projects_data(researcher, csv_filename, year)
