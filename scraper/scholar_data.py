#!/user/bin/env python3

from __future__ import unicode_literals
import requests
import scholarly

_EXACT_SEARCH = '/scholar?q="{}"'
_START_YEAR = '&as_ylo={}'
_END_YEAR = '&as_yhi={}'


def get_published_papers(start_year=None, end_year=None):
    """ Returns a generator that returns dicts with paper metadata."""
    query = "Cure Alzheimer's Fund"
    url = _EXACT_SEARCH.format(requests.utils.quote(query))
    if start_year:
        url += _START_YEAR.format(start_year)
    if end_year:
        url += _END_YEAR.format(end_year)
    soup = scholarly._get_soup(url)
    return scholarly._search_scholar_soup(soup)
