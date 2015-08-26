# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('demoapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'Equipment')),
            ],
        ),
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(max_length=254, verbose_name=b'Email'),
        ),
        migrations.AlterField(
            model_name='person',
            name='sdate',
            field=models.DateField(verbose_name=b'Start date'),
        ),
        migrations.AddField(
            model_name='equipment',
            name='person',
            field=models.ForeignKey(to='demoapp.Person'),
        ),
    ]
