# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-05 11:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bonghwa', '0004_auto_20171105_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='contents',
            name='file',
            field=models.FileField(null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='contents',
            name='imagename',
            field=models.CharField(default='', max_length=150),
        ),
    ]