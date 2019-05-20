# Generated by Django 2.1.7 on 2019-05-20 01:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('replayanalysis', '0002_auto_20190516_2105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manual_replay',
            name='t1pokemon1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team1Pokemon1', to='pokemondatabase.all_pokemon'),
        ),
        migrations.AlterField(
            model_name='manual_replay',
            name='t1pokemon2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team1Pokemon2', to='pokemondatabase.all_pokemon'),
        ),
        migrations.AlterField(
            model_name='manual_replay',
            name='t1pokemon3',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team1Pokemon3', to='pokemondatabase.all_pokemon'),
        ),
        migrations.AlterField(
            model_name='manual_replay',
            name='t1pokemon4',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team1Pokemon4', to='pokemondatabase.all_pokemon'),
        ),
        migrations.AlterField(
            model_name='manual_replay',
            name='t1pokemon5',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team1Pokemon5', to='pokemondatabase.all_pokemon'),
        ),
        migrations.AlterField(
            model_name='manual_replay',
            name='t1pokemon6',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team1Pokemon6', to='pokemondatabase.all_pokemon'),
        ),
        migrations.AlterField(
            model_name='manual_replay',
            name='t2pokemon1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team2Pokemon1', to='pokemondatabase.all_pokemon'),
        ),
        migrations.AlterField(
            model_name='manual_replay',
            name='t2pokemon2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team2Pokemon2', to='pokemondatabase.all_pokemon'),
        ),
        migrations.AlterField(
            model_name='manual_replay',
            name='t2pokemon3',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team2Pokemon3', to='pokemondatabase.all_pokemon'),
        ),
        migrations.AlterField(
            model_name='manual_replay',
            name='t2pokemon4',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team2Pokemon4', to='pokemondatabase.all_pokemon'),
        ),
        migrations.AlterField(
            model_name='manual_replay',
            name='t2pokemon5',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team2Pokemon5', to='pokemondatabase.all_pokemon'),
        ),
        migrations.AlterField(
            model_name='manual_replay',
            name='t2pokemon6',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Team2Pokemon6', to='pokemondatabase.all_pokemon'),
        ),
    ]