from django.test import TestCase
from scraper.management.commands import scrape
from scraper import nih_data
from scraper.models import Author, Paper

class DummyPublication(object):
    def fill(self):
        pass
    def __init__(self, title, citations, authors, url=None, year=None,
                 abstract=None, volume=None, issue=None):
        self.bib = {}
        self.bib['title'] = title
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
        if url:
            self.bib['url'] = url

# Create your tests here.
class ScrapeTestCase(TestCase):
    def test_scraping(self):
        p1 = DummyPublication(
            'Hats and Stuff', 63, 'Hats, Bob and Hats, Billy',
            url='example.com',
            abstract='About hats and stuff',
            year=1992,
            volume=1)
        p2 = DummyPublication(
            'Hats and Other Stuff', 36, 'Tanzi, Rudolph',
            url='example.com',
            abstract='More about hats and stuff',
            year=2015,
            volume=1)
        p3 = DummyPublication(
            'No Abstract or website: Reviewed', 0, 'Bob, Billy',
            year=2015)
        p4 = DummyPublication(
            'No Year: Revisited', 12, 'Bob, Billy and others',
            url='example.com')
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
        self.assertEqual(len(query), 3)
        query = Author.objects.filter(name='others')
        self.assertEqual(len(query), 0)

    def test_unicode(self):
        p = DummyPublication(
            'Converting Bibtex to Unicode', 12, r'Unic{\o}der, J{\o}rgen H')
        command = scrape.Command()
        command.handle_publication(p, 2015)
        author = Author.objects.all()[0]
        self.assertEqual(author.name, "Unicøder, Bøb H")
