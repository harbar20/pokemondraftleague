# Generated by Django 2.1.7 on 2019-07-15 21:44

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('individualleague', '0018_pickemleaderboard'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='pickemleaderboard',
            new_name='pickem_leaderboard',
        ),
    ]
