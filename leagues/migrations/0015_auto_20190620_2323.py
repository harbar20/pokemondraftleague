# Generated by Django 2.1.7 on 2019-06-20 23:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0014_seasonsetting_playoffteamsperconference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conference_name',
            name='league',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conferences', to='leagues.league'),
        ),
    ]
