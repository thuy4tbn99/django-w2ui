# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fname', models.CharField(max_length=200, verbose_name=b'First name')),
                ('lname', models.CharField(max_length=200, verbose_name=b'Last name')),
                ('email', models.EmailField(max_length=254)),
                ('sdate', models.DateField()),
            ],
        ),
    ]
