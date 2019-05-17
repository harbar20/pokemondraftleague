# Generated by Django 2.1.7 on 2019-05-17 03:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0026_auto_20190515_1615'),
        ('individualleague', '0005_auto_20190507_0139'),
    ]

    operations = [
        migrations.CreateModel(
            name='free_agency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekeffective', models.IntegerField(default=1)),
                ('addedpokemon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='added', to='leagues.roster')),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leagues.coachdata')),
                ('droppedpokemon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dropped', to='leagues.roster')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leagues.seasonsetting')),
            ],
        ),
    ]
