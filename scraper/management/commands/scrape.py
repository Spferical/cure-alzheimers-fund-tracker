from django.core.management.base import BaseCommand
from scraper import scholar_data
from scraper import nih_data
from scraper.models import Paper, Author


class Command(BaseCommand):
    def handle_publication(self, publication):
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
                abstract=publication.bib['abstract'],
                year=int(publication.bib['year']))
        else:
            paper = query[0]

        try:
            paper.volume = publication.bib['volume']
        except KeyError:
            pass
        try:
            paper.issue = publication.bib['issue']
        except KeyError:
            pass
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

    def handle(self, *args, **options):
        # get total number of citations
        # also get a list of funded authors
        self.stdout.write("GETTING ALL PAPERS")
        publications = list(scholar_data.get_published_papers())
        self.stdout.write("ALL PAPERS GOTTEN, FILLING INFO FOR EACH")
        for publication in publications:
            self.handle_publication(publication)

        self.stdout.write('\n' * 4)
        self.stdout.write('#' * 10)
        self.stdout.write('\n' * 4)

        nih_data.scrape('2015')

