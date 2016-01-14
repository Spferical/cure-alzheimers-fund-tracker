import re
import requests
import scholarly

_EXACT_SEARCH = '/scholar?q="{}"'
_START_YEAR = '&as_ylo={}'
_END_YEAR = '&as_yhi={}'


class Papers(object):
    """Wrapper around scholarly._search_scholar_soup that allows one to get the
    number of papers found in the search with len()"""
    def __init__(self, query, start_year=None, end_year=None):
        url = _EXACT_SEARCH.format(requests.utils.quote(query))
        if start_year:
            url += _START_YEAR.format(start_year)
        if end_year:
            url += _END_YEAR.format(end_year)
        soup = scholarly._get_soup(url)
        results = soup.find('div', id='gs_ab_md').text
        self.num = int(re.search(r'\d+ results', results).group(0).split()[0])

        self.papers = scholarly._search_scholar_soup(soup)

    def __len__(self):
        return self.num

    def __iter__(self):
        return (paper.fill().bib for paper in self.papers)


def get_published_papers():
    """ Returns a generator that returns dicts with paper metadata."""
    return Papers("Cure Alzheimer's Fund", start_year=2015, end_year=2015)


def main():
    papers = get_published_papers()
    print("Number of results:", len(papers))
    for paper in papers:
        stuff = ['title', 'author', 'journal', 'volume', 'issue']
        for thing in stuff:
            if thing in paper:
                print("{}: {}".format(thing, paper[thing]))

if __name__ == '__main__':
    main()

