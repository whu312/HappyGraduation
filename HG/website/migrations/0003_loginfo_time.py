# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-04-20 12:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_auto_20160420_1906'),
    ]

    operations = [
        migrations.AddField(
            model_name='loginfo',
            name='time',
            field=models.CharField(default=1, max_length=128),
            preserve_default=False,
        ),
    ]