from django.test import TestCase
from scraper.management.commands import scrape
from scraper import nih_data
from scraper.models import Paper

class DummyPublication(object):
    def fill(self):
        pass
    def __init__(self, title, url, citations, authors, year=None,
                 abstract=None, volume=None, issue=None):
        self.bib = {}
        self.bib['title'] = title
        self.bib['url'] = url
        self.citedby = citations
        self.bib['author'] = authors
        if year:
            self.bib['year'] = year
        if abstract:
            self.bib['abstract'] = abstract
        if volume:
            self.volume = volume
        if issue:
            self.issue = issue

# Create your tests here.
class ScrapeTestCase(TestCase):
    def test_scraping(self):
        p1 = DummyPublication(
            'Hats and Stuff', 'example.com', 63,
            'Hats, Bob and Hats, Billy', 'About hats and stuff', 1992, 1)
        p2 = DummyPublication(
            'Hats and Other Stuff', 'example.com',
            36, 'Tanzi, Rudolph', 'More about hats and stuff', 2015, 1)
        p3 = DummyPublication(
            'No Abstract: Reviewed', 'example.com', 0, 'Bob, Billy', 2015)
        p4 = DummyPublication(
            'No Year: Revisited', 'example.com', 12, 'Bob, Billy')
        command = scrape.Command()
        command.handle_publication(p1, 1992)
        command.handle_publication(p2, 2015)
        command.handle_publication(p3, 2015)
        command.handle_publication(p4, 2014)
        nih_data.scrape('1992')
        nih_data.scrape('2015')

        for paper in Paper.objects.filter(citations=36):
            self.assertEqual(paper.title, 'Hats and Other Stuff')
            self.assertEqual(paper.year, 2015)
        query = Paper.objects.filter(url='example.com')
        self.assertEqual(len(query), 4)
