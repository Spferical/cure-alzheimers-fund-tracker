from __future__ import unicode_literals
from django.db import models


class Author(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class FundedAuthor(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Paper(models.Model):
    url = models.TextField()
    title = models.TextField()
    citations = models.IntegerField()
    abstract = models.TextField()
    journal = models.TextField()
    volume = models.IntegerField(null=True)
    issue = models.IntegerField(null=True)
    year = models.IntegerField()
    authors = models.ManyToManyField(Author)
    class Meta:
        ordering = ['year', 'title']


class Project(models.Model):
    researcher = models.ForeignKey(FundedAuthor)
    title = models.TextField()
    url = models.TextField()
    funding_amount = models.IntegerField()
    year = models.IntegerField()
    class Meta:
        ordering = ['year', 'title']
