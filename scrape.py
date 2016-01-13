import scholarly
import requests

_SEARCH = '/scholar?q=\"{}\"&as_ylo={}&as_yhi={}'
def search(query, start_year, end_year):
    """Search by scholar query and return a generator of Publication objects"""
    soup = scholarly._get_soup(
        _SEARCH.format(requests.utils.quote(query),
                       str(start_year), str(end_year)))
    return scholarly._search_scholar_soup(soup)

if __name__ == '__main__':
    s = search("Cure Alzheimer's Fund", 2015, 2015)
    num = 0
    for x in s:
        x.fill()
        stuff = ['title', 'author', 'journal', 'volume', 'issue']
        for thing in stuff:
            if thing in x.bib:
                print("{}: {}".format(thing, x.bib[thing]))
        num += 1

    print("Number of results:", num)
