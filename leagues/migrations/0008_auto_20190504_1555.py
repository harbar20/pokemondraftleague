# Generated by Django 2.1.7 on 2019-05-04 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0007_league_settings_draftbudget'),
    ]

    operations = [
        migrations.AlterField(
            model_name='award',
            name='awardname',
            field=models.CharField(default='None', max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='league',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]