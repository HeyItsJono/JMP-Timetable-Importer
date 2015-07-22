# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NumQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question_text', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='PBLQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question_text', models.CharField(max_length=200)),
            ],
        ),
        migrations.AlterField(
            model_name='numchoice',
            name='question',
            field=models.ForeignKey(to='timetable.NumQuestion'),
        ),
        migrations.AlterField(
            model_name='pblchoice',
            name='question',
            field=models.ForeignKey(to='timetable.PBLQuestion'),
        ),
    ]
