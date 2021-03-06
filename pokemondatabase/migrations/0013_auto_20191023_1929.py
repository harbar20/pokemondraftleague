# Generated by Django 2.1.7 on 2019-10-23 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemondatabase', '0012_all_pokemon_nicknames'),
    ]

    operations = [
        migrations.AddField(
            model_name='all_pokemon',
            name='damagedone',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='all_pokemon',
            name='hphealed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='all_pokemon',
            name='luck',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='all_pokemon',
            name='remaininghealth',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='all_pokemon',
            name='support',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokemon_leaderboard',
            name='damagedone',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokemon_leaderboard',
            name='hphealed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokemon_leaderboard',
            name='luck',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='pokemon_leaderboard',
            name='remaininghealth',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pokemon_leaderboard',
            name='support',
            field=models.IntegerField(default=0),
        ),
    ]
