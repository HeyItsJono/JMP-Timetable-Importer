# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NumChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice_number', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='PBLChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice_text', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question_text', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='pblchoice',
            name='question',
            field=models.ForeignKey(to='timetable.Question'),
        ),
        migrations.AddField(
            model_name='numchoice',
            name='question',
            field=models.ForeignKey(to='timetable.Question'),
        ),
    ]
