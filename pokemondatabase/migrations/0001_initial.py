# Generated by Django 2.1.7 on 2019-05-03 00:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='all_pokemon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pokemon', models.CharField(max_length=30)),
                ('hp', models.IntegerField()),
                ('attack', models.IntegerField()),
                ('defense', models.IntegerField()),
                ('s_attack', models.IntegerField()),
                ('s_defense', models.IntegerField()),
                ('speed', models.IntegerField()),
                ('is_fully_evolved', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='moveinfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('move_typing', models.CharField(max_length=10)),
                ('move_category', models.CharField(max_length=10)),
                ('move_power', models.IntegerField()),
                ('move_accuracy', models.IntegerField()),
                ('move_priority', models.IntegerField()),
                ('secondary_effect_chance', models.IntegerField()),
                ('secondary_effect', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='pokemon_ability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ability', models.CharField(max_length=30)),
                ('pokemon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pokemondatabase.all_pokemon')),
            ],
        ),
        migrations.CreateModel(
            name='pokemon_moveset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('moveinfo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pokemondatabase.moveinfo')),
                ('pokemon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pokemondatabase.all_pokemon')),
            ],
        ),
        migrations.CreateModel(
            name='pokemon_tier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(default=0)),
                ('pokemon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pokemondatabase.all_pokemon')),
            ],
        ),
        migrations.CreateModel(
            name='pokemon_type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typing', models.CharField(max_length=15)),
                ('pokemon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pokemondatabase.all_pokemon')),
            ],
        ),
    ]