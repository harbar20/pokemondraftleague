# Generated by Django 2.2.10 on 2020-04-20 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0075_auto_20200411_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='league_configuration',
            name='allows_cross_subleague_matches',
            field=models.BooleanField(default=False),
        ),
    ]
