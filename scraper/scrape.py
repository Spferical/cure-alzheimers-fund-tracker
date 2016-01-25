#!/user/bin/env python3

import re
import requests
import scholarly
from pprint import pprint
import nih_data

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
        return self.papers


def get_published_papers(start_year=None, end_year=None):
    """ Returns a generator that returns dicts with paper metadata."""
    return Papers("Cure Alzheimer's Fund",
                  start_year=start_year, end_year=end_year)


def main():
    # get data about papers published in 2015
    print("PAPERS PUBLISHED IN 2015 CONTAINING THE EXACT WORDS \"CURE ALZHEIMER'S FUND\"")
    papers = get_published_papers(2015, 2015)
    print("Number of results:", len(papers))
    for paper in papers:
        paper.fill()
        print("-" * 10)
        stuff = ['title', 'author', 'journal', 'volume', 'issue']
        meta_to_data = dict()
        for thing in stuff:
            if thing in paper.bib:
                meta_to_data[thing] = paper.bib[thing]
        pprint(meta_to_data)

    print('\n' * 4)
    print('#' * 10)
    print('\n' * 4)

    # get total number of citations
    # also get a list of funded authors
    print("GETTING AUTHORS & TOTAL NUMBER OF CITATIONS...")
    papers_all = list(get_published_papers())
    print("ALL PAPERS GOTTEN, FILLING INFO FOR EACH")
    total_citations = 0
    authors = []
    for paper in papers_all:
        print('-' * 10)
        paper.fill()
        print(paper.bib['title'])
        print("Authors: " + paper.bib['author'])
        authors.extend(paper.bib['author'].split(' and '))
        try:
            print("Cited", str(paper.citedby), "times")
            total_citations += paper.citedby
        except AttributeError:
            print("Cited 0 times")
    print('\n' * 4)
    print('#' * 10)
    print('\n' * 4)
    print(
        "TOTAL CITATIONS OF PAPERS CONTAINING THE EXACT WORDS \"CURE ALZHEIMER'S FUND\":",
        total_citations)

    # now we can get the NIH grants for each author
    print("Authors:")
    for author in authors:
        print(author)
    nih_data.scrape(authors, '2015')

if __name__ == '__main__':
    main()
