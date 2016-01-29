from __future__ import unicode_literals
from datetime import date
from django.core.management.base import BaseCommand
from scraper import nih_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        for year in range(2007, date.today().year):
            nih_data.scrape(str(year))

