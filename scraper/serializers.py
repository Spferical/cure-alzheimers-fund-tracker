from __future__ import unicode_literals
from rest_framework import serializers
from scraper.models import Author, Paper, Project


class AuthorSerializer(serializers.ModelSerializer):
	"""
	Serializes authors
	"""

	class Meta:
		model = Author
		fields = ('name',)


class PaperSerializer(serializers.ModelSerializer):
	"""
	Serializes papers
	"""
	authors = serializers.StringRelatedField(many=True)

	class Meta:
		model = Paper
		fields = ('url', 'title', 'citations', 'abstract', 'journal', 'volume', 'issue', 'year', 'authors', 'id',)


class ProjectSerializer(serializers.ModelSerializer):
	"""
	Serializes projects
	"""
	researcher = serializers.StringRelatedField()

	class Meta:
		model = Project
		fields = ('researcher', 'title', 'url', 'funding_amount', 'year', 'id',)