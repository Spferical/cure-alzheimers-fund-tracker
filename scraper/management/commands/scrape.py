from datetime import date
import pickle
import os
import itertools
from bibtexparser.latexenc import unicode_to_latex, unicode_to_crappy_latex1, \
    unicode_to_crappy_latex2
from django.core.management.base import BaseCommand
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
        title = convert_to_unicode(publication.bib['title'])
        query = Paper.objects.filter(title=title)
        if not query:
            # we haven't saved this paper yet!
            paper = Paper(
                title=title,
                citations=num_citations,
                year=year)
        else:
            paper = query[0]

        if 'url' in publication.bib:
            paper.url = publication.bib['url']
        else:
            paper.url = ''
        if 'volume' in publication.bib:
            paper.volume = publication.bib['volume']
        if 'issue' in publication.bib:
            paper.issue = publication.bib['issue']
        if 'abstract' in publication.bib:
            paper.abstract = convert_to_unicode(publication.bib['abstract'])
        paper.save()
        self.stdout.write(publication.bib['title'])
        self.stdout.write("Authors: " + publication.bib['author'])
        for name in publication.bib['author'].split(' and '):
            if self.is_bad(name):
                continue
            name = convert_to_unicode(name)
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
                except:
                    self.abort(publications)
                    raise

        self.stdout.write("ALL PAPERS GOTTEN, FILLING INFO FOR EACH")
        for year in publications:
            for publication in publications[year][:]:
                try:
                    self.handle_publication(publication, year)
                    publications[year].remove(publication)
                except:
                    self.abort(publications)
                    raise
        self.stdout.write('\n' * 4)
        self.stdout.write('#' * 10)
        self.stdout.write('\n' * 4)

        for year in range(2007, date.today().year):
            nih_data.scrape(str(year))

    def is_bad(self, name):
        return name in ['other', 'others']

def convert_to_unicode(text):
    """
    Convert accent from latex to unicode style.
    Returns the modified text.
    """
    # modified from python-bibtexparser convert_to_unicode function
    # see https://github.com/sciunto-org/python-bibtexparser/
    if '\\' in text or '{' in text:
        for k, v in itertools.chain(unicode_to_crappy_latex1, unicode_to_latex):
            if v in text:
                text = text.replace(v, k)

    # If there is still very crappy items
    if '\\' in text:
        for k, v in unicode_to_crappy_latex2:
            if v in text:
                parts = text.split(str(v))
                for key, text in enumerate(parts):
                    if key+1 < len(parts) and len(parts[key+1]) > 0:
                        # Change order to display accents
                        parts[key] = parts[key] + parts[key+1][0]
                        parts[key+1] = parts[key+1][1:]
                text = k.join(parts)
    return text
