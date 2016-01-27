from django.test import TestCase
from scraper.management.commands import scrape
from scraper import nih_data
from scraper.models import Paper

class DummyPublication(object):
    def fill(self):
        pass
    def __init__(self, title, url, abstract, citations, authors, year,
                 volume=None, issue=None):
        self.bib = {}
        self.bib['title'] = title
        self.bib['url'] = url
        self.bib['abstract'] = abstract
        self.citedby = citations
        self.bib['author'] = authors
        self.bib['year'] = year
        if volume:
            self.volume = volume
        if issue:
            self.issue = issue

# Create your tests here.
class ScrapeTestCase(TestCase):
    def test_scraping(self):
        p1 = DummyPublication(
            'Hats and Stuff', 'example.com', 'About hats and stuff', 63,
            'Hats, Bob and Hats, Billy', 1992, 1)
        p2 = DummyPublication(
            'Hats and Other Stuff', 'example.com', 'More about hats and stuff',
            36, 'Tanzi, Rudolph', 2015, 1)
        command = scrape.Command()
        command.handle_publication(p1)
        command.handle_publication(p2)
        nih_data.scrape('1992')

        for paper in Paper.objects.filter(citations=36):
            self.assertEqual(paper.title, 'Hats and Other Stuff')
            self.assertEqual(paper.year, 2015)
        query = Paper.objects.filter(url='example.com')
        self.assertEqual(len(query), 2)
