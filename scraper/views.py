from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader
from rest_framework import viewsets, mixins
from scraper.serializers import AuthorSerializer, PaperSerializer, ProjectSerializer
from scraper.models import Author, Paper, Project


def index(request):
	template = loader.get_template("index.html")
	return HttpResponse(template.render())


class AuthorViewSet(viewsets.ModelViewSet):
	"""
	API endpoint to access authors
	"""
	queryset = Author.objects.all()
	serializer_class = AuthorSerializer


class PaperViewSet(viewsets.ModelViewSet):
	"""
	API endpoint to access papers
	"""
	queryset = Paper.objects.all()
	serializer_class = PaperSerializer


class ProjectViewSet(viewsets.ModelViewSet):
	"""
	API endpoint to access projects
	"""
	queryset = Project.objects.all()
	serializer_class = ProjectSerializer
