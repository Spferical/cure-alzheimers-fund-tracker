import scholarly
import requests

_EXACT_SEARCH = '/scholar?q="{}"'
_START_YEAR = '&as_ylo={}'
_END_YEAR = '&as_yhi={}'
def search(query, exact=True, start_year=None, end_year=None):
    """Search by scholar query and return a generator of Publication objects"""
    url = _EXACT_SEARCH.format(requests.utils.quote(query))
    if start_year:
        url += _START_YEAR.format(start_year)
    if end_year:
        url += _END_YEAR.format(end_year)
    soup = scholarly._get_soup(url)
    return scholarly._search_scholar_soup(soup)

if __name__ == '__main__':
    s = search("Cure Alzheimer's Fund", start_year=2015, end_year=2015)
    num = 0
    for x in s:
        x.fill()
        stuff = ['title', 'author', 'journal', 'volume', 'issue']
        for thing in stuff:
            if thing in x.bib:
                print("{}: {}".format(thing, x.bib[thing]))
        num += 1

    print("Number of results:", num)
