# Generated by Django 2.2.10 on 2020-06-18 19:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pokemondatabase', '0033_auto_20200618_1928'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='preevolution',
            unique_together={('pokemon', 'preevo')},
        ),
    ]
