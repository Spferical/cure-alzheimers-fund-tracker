# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-27 02:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0002_auto_20160127_0220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paper',
            name='issue',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='paper',
            name='volume',
            field=models.IntegerField(null=True),
        ),
    ]
