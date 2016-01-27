from django.db import models


class Author(models.Model):
    name = models.TextField()


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


class Project(models.Model):
    researcher = models.ForeignKey(Author)
    title = models.TextField()
    url = models.TextField()
    funding_amount = models.IntegerField()
