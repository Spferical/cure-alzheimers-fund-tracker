from django.core.management.base import BaseCommand
from datetime import date
import pickle
import os
from scraper import scholar_data
from scraper import nih_data
from scraper.models import Paper, Author


PROGRESS_FILE = 'scrape_progress.db'

class Command(BaseCommand):
    def handle_publication(self, publication, year):
        self.stdout.write('-' * 10)
        publication.fill()
        try:
            num_citations = publication.citedby
        except AttributeError:
            num_citations = 0
        self.stdout.write("Cited " + str(num_citations) + " times")
        # check to see if we already saved this publication or not
        query = Paper.objects.filter(title=publication.bib['title'])
        if not query:
            # we haven't saved this paper yet!
            paper = Paper(
                url=publication.bib['url'],
                title=publication.bib['title'],
                citations=num_citations,
                year=year)
        else:
            paper = query[0]

        if 'volume' in publication.bib:
            paper.volume = publication.bib['volume']
        if 'issue' in publication.bib:
            paper.issue = publication.bib['issue']
        if 'abstract' in publication.bib:
            paper.abstract = publication.bib['abstract']
        paper.save()
        self.stdout.write(publication.bib['title'])
        self.stdout.write("Authors: " + publication.bib['author'])
        for name in publication.bib['author'].split(' and '):
            query = Author.objects.filter(name=name)
            if not query:
                # this is a new author
                author = Author(name=name)
                author.save()
            else:
                author = query[0]
            if not paper.authors.filter(name=name):
                paper.authors.add(author)

    def abort(self, publications):
        # pickle everything unhandled and try again later
        self.stdout.write("SOMETHING WENT WRONG: SAVING PROGRESS")
        with open(PROGRESS_FILE, 'wb') as progress_file:
            pickle.dump(publications, progress_file)

    def handle(self, *args, **options):
        # {year : publications}
        publications = {}
        if os.path.isfile(PROGRESS_FILE):
            # load our previous progress, if any
            with open(PROGRESS_FILE, 'rb') as progress_file:
                publications = pickle.load(progress_file)
            # remove it for now --
            # if anything goes wrong, we'll save it again!
            os.remove(PROGRESS_FILE)

        for year in range(2007, date.today().year):
            if not year in publications:
                self.stdout.write("GETTING PAPERS FOR YEAR " + str(year))
                try:
                    publications[year] = \
                        list(scholar_data.get_published_papers(year, year))
                except Exception:
                    self.abort(publications)
                    raise

        self.stdout.write("ALL PAPERS GOTTEN, FILLING INFO FOR EACH")
        for year in publications:
            for publication in publications[year][:]:
                try:
                    self.handle_publication(publication, year)
                    publications[year].remove(publication)
                except Exception:
                    self.abort(publications)
                    raise
        self.stdout.write('\n' * 4)
        self.stdout.write('#' * 10)
        self.stdout.write('\n' * 4)

        nih_data.scrape('2015')

