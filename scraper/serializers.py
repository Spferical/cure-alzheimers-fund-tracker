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

	class Meta:
		model = Paper
		fields = ('url', 'title', 'citations', 'abstract', 'journal', 'volume', 'issue', 'year', 'authors',)


class ProjectSerializer(serializers.ModelSerializer):
	"""
	Serializes projects
	"""

	class Meta:
		model = Paper
		fields = ('researcher', 'title', 'url', 'funding_amount',)