# Generated by Django 2.1.7 on 2019-07-03 13:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('individualleague', '0008_auto_20190628_1817'),
    ]

    operations = [
        migrations.CreateModel(
            name='freeagency_announcements',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league', models.CharField(max_length=100)),
                ('league_name', models.CharField(max_length=100)),
                ('text', models.CharField(max_length=1000)),
                ('freeagencychannel', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='replay_announcements',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league', models.CharField(max_length=100)),
                ('league_name', models.CharField(max_length=100)),
                ('text', models.CharField(max_length=1000)),
                ('replaychannel', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='trading_announcements',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league', models.CharField(max_length=100)),
                ('league_name', models.CharField(max_length=100)),
                ('text', models.CharField(max_length=1000)),
                ('tradingchannel', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='schedule',
            name='season',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedule', to='leagues.seasonsetting'),
        ),
    ]
