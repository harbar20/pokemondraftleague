# Generated by Django 2.2.10 on 2020-06-10 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemondatabase', '0025_auto_20200406_2347'),
    ]

    operations = [
        migrations.AddField(
            model_name='moveinfo',
            name='crits',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='moveinfo',
            name='hits',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='moveinfo',
            name='posssecondaryeffects',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='moveinfo',
            name='secondaryeffects',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='moveinfo',
            name='uses',
            field=models.IntegerField(default=0),
        ),
    ]