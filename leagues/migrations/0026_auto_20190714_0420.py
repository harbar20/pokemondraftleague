# Generated by Django 2.1.7 on 2019-07-14 04:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0025_auto_20190714_0419'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coachaward',
            options={'ordering': ['award__ordering']},
        ),
    ]
