# Generated by Django 2.1.7 on 2019-07-03 13:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0022_auto_20190628_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coachdata',
            name='parent_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_teams', to='leagues.league_team'),
        ),
    ]
