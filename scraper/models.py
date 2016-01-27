from django.db import models

class Paper(models.Model):
    url = models.TextField()
    title = models.TextField()
    citations = models.IntegerField()
    abstract = models.TextField()
    journal = models.TextField()
    volume = models.IntegerField()
    date = models.DateField()

class Author(models.Model):
    papers = models.ManyToManyField(Paper)
