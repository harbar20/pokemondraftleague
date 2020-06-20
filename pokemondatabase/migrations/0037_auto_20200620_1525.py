# Generated by Django 2.2.10 on 2020-06-20 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pokemondatabase', '0036_auto_20200619_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pokemon_movedata',
            name='pokemon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pokemon_movedata', to='pokemondatabase.all_pokemon'),
        ),
        migrations.AlterUniqueTogether(
            name='pokemon_tier_template',
            unique_together={('pokemon', 'template')},
        ),
    ]
