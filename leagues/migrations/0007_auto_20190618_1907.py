# Generated by Django 2.1.7 on 2019-06-18 19:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0006_auto_20190617_1941'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='draft',
            options={'ordering': ['id']},
        ),
    ]