# Generated by Django 2.1.7 on 2019-05-15 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0024_seasonsetting_numzusers'),
    ]

    operations = [
        migrations.AddField(
            model_name='roster',
            name='candeletez',
            field=models.BooleanField(default=False),
        ),
    ]