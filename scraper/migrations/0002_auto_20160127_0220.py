# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-27 02:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('url', models.TextField()),
                ('funding_amount', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='author',
            name='papers',
        ),
        migrations.RemoveField(
            model_name='paper',
            name='date',
        ),
        migrations.AddField(
            model_name='author',
            name='name',
            field=models.TextField(default='(dummy)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paper',
            name='authors',
            field=models.ManyToManyField(to='scraper.Author'),
        ),
        migrations.AddField(
            model_name='paper',
            name='issue',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paper',
            name='year',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='researcher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scraper.Author'),
        ),
    ]